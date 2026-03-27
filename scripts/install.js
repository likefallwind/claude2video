#!/usr/bin/env node
/**
 * claude2video skill installer
 *
 * Copies the skill files into the target project's .agents/skills/claude2video/
 *
 * Usage:
 *   npm install claude2video          # auto-runs via postinstall
 *   npx claude2video                  # run directly
 *   npx claude2video --global         # install to ~/.claude/agents/skills/
 */

const fs = require('fs');
const path = require('path');

const SKILL_NAME = 'claude2video';

// Source: skill files bundled inside this npm package
const pkgDir = path.resolve(__dirname, '..');
const skillSrc = path.join(pkgDir, '.agents', 'skills', SKILL_NAME);

// Destination: determined by context
function getTarget() {
  const args = process.argv.slice(2);
  if (args.includes('--global')) {
    const home = process.env.HOME || process.env.USERPROFILE;
    return path.join(home, '.claude', 'skills', SKILL_NAME);
  }

  const cwd = process.cwd();

  if (cwd !== pkgDir) {
    // Running via npx — cwd is the user's project directory
    return path.join(cwd, '.agents', 'skills', SKILL_NAME);
  }

  // cwd === pkgDir: either npm postinstall of a dependency, or local dev
  // Detect npm dependency install: pkgDir will contain /node_modules/<pkg>
  const nmMarker = path.sep + 'node_modules' + path.sep;
  const nmIdx = pkgDir.lastIndexOf(nmMarker);
  if (nmIdx !== -1) {
    // Installed as a dependency — consumer project root is before node_modules
    const consumerRoot = pkgDir.substring(0, nmIdx);
    return path.join(consumerRoot, '.agents', 'skills', SKILL_NAME);
  }

  // Running inside the package source itself (local dev) — no-op
  return null;
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function main() {
  const target = getTarget();
  if (!target) {
    console.log(`[claude2video] Development install — skipping skill copy.`);
    return;
  }

  if (!fs.existsSync(skillSrc)) {
    console.error(`[claude2video] Skill source not found: ${skillSrc}`);
    process.exit(1);
  }

  try {
    copyDir(skillSrc, target);

    // Also copy setup.sh so it's accessible from the target directory
    const setupSrc = path.join(pkgDir, 'setup.sh');
    if (fs.existsSync(setupSrc)) {
      const setupDest = path.join(target, 'setup.sh');
      fs.copyFileSync(setupSrc, setupDest);
      fs.chmodSync(setupDest, 0o755);
    }

    console.log(`\n[claude2video] Skill installed to: ${target}`);
    console.log(`\nNext step — install Python/system dependencies:`);
    console.log(`  bash ${path.join(target, 'setup.sh')}\n`);
  } catch (err) {
    console.error(`[claude2video] Install failed: ${err.message}`);
    process.exit(1);
  }
}

main();
