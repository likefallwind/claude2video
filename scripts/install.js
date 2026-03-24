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

  // When running as postinstall, cwd is the package root itself — skip
  // (we only want to install into the *consumer* project, not ourselves)
  const cwd = process.cwd();
  if (cwd === pkgDir) {
    // Running postinstall inside the skill package itself — no-op
    return null;
  }

  return path.join(cwd, '.agents', 'skills', SKILL_NAME);
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
    console.log(`\n[claude2video] Skill installed to: ${target}`);
    console.log(`\nNext step — install Python/system dependencies:`);
    console.log(`  bash node_modules/claude2video/setup.sh\n`);
  } catch (err) {
    console.error(`[claude2video] Install failed: ${err.message}`);
    process.exit(1);
  }
}

main();
