#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const request = JSON.parse(fs.readFileSync(0, "utf8"));
const packageRoot = path.resolve(request.typescript);
const apiModule = await import(pathToFileURL(path.join(packageRoot, "dist/api/sync/api.js")));
const ts = await import(pathToFileURL(path.join(packageRoot, "dist/ast/index.js")));
const version = JSON.parse(fs.readFileSync(path.join(packageRoot, "package.json"), "utf8")).version;

function nameOf(node) {
  if (!node) return null;
  if (ts.isIdentifier(node) || ts.isStringLiteral(node)) return node.text;
  return node.getText();
}

function callName(expression) {
  if (ts.isIdentifier(expression)) return expression.text;
  if (ts.isPropertyAccessExpression(expression)) return `${expression.expression.getText()}.${expression.name.text}`;
  return expression.getText();
}

function extract(source) {
  const symbols = [];
  const imports = [];
  const calls = [];
  const scopes = [];
  const namedExpressions = new Map();
  const line = node => source.getLineAndCharacterOfPosition(node.getStart()).line + 1;

  function visit(node) {
    let entered = false;
    if (ts.isFunctionDeclaration(node) || ts.isClassDeclaration(node) || ts.isMethodDeclaration(node)) {
      const name = nameOf(node.name);
      if (name) {
        symbols.push({
          name,
          qualified: [...scopes, name].join("."),
          kind: ts.isClassDeclaration(node) ? "class" : ts.isMethodDeclaration(node) ? "method" : "function",
          line: line(node),
        });
        scopes.push(name);
        entered = true;
      }
    }
    if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) && node.initializer &&
        (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer))) {
      const name = node.name.text;
      symbols.push({name, qualified: [...scopes, name].join("."), kind: "function", line: line(node)});
      namedExpressions.set(node.initializer, name);
    }
    if ((ts.isArrowFunction(node) || ts.isFunctionExpression(node)) && namedExpressions.has(node)) {
      scopes.push(namedExpressions.get(node));
      entered = true;
    }
    if (ts.isImportDeclaration(node) && ts.isStringLiteral(node.moduleSpecifier)) {
      const bindings = [];
      const clause = node.importClause;
      if (clause?.name) bindings.push({local: clause.name.text, imported: "default", kind: "default"});
      if (clause?.namedBindings) {
        if (ts.isNamespaceImport(clause.namedBindings)) {
          bindings.push({local: clause.namedBindings.name.text, imported: "*", kind: "namespace"});
        } else {
          for (const item of clause.namedBindings.elements) {
            bindings.push({local: item.name.text, imported: item.propertyName?.text || item.name.text, kind: "named"});
          }
        }
      }
      imports.push({module: node.moduleSpecifier.text, bindings, line: line(node)});
    }
    if (ts.isCallExpression(node)) {
      calls.push({caller: scopes.join(".") || null, expression: callName(node.expression), line: line(node)});
    }
    node.forEachChild(visit);
    if (entered) scopes.pop();
  }

  visit(source);
  return {symbols, imports, calls};
}

const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "repo-code-graph-"));
let api;
try {
  for (const file of request.files) {
    const output = path.join(temporary, file.path);
    fs.mkdirSync(path.dirname(output), {recursive: true});
    fs.writeFileSync(output, file.content);
  }
  const config = path.join(temporary, "tsconfig.json");
  fs.writeFileSync(config, JSON.stringify({
    compilerOptions: {allowJs: true, checkJs: false, jsx: "preserve", noLib: true, noResolve: true},
    include: request.files.map(file => file.path),
  }));
  api = new apiModule.API({cwd: temporary});
  const snapshot = api.updateSnapshot({openProjects: [config]});
  const project = snapshot.getProject(config) || snapshot.getProjects()[0];
  if (!project) throw new Error("TypeScript compiler did not create a project");
  const outputs = request.files.map(file => {
    const absolute = path.join(temporary, file.path);
    const source = project.program.getSourceFile(absolute);
    if (!source) throw new Error(`TypeScript compiler omitted ${file.path}`);
    const diagnostics = project.program.getSyntacticDiagnostics(absolute).map(item => String(item.messageText));
    return {path: file.path, ...extract(source), diagnostics};
  });
  snapshot.dispose();
  process.stdout.write(JSON.stringify({typescript_version: version, files: outputs}));
} finally {
  api?.close();
  fs.rmSync(temporary, {recursive: true, force: true});
}
