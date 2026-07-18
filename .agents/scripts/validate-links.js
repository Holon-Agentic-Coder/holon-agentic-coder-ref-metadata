const fs = require('fs');
const path = require('path');

// Root folder of the repository
const rootDir = path.resolve(__dirname, '../..');

// Files to check
const filesToCheck = [
  path.join(rootDir, 'README.md'),
  path.join(rootDir, 'AGENTS.md'),
  path.join(rootDir, '.agents/instructions.md'),
  path.join(rootDir, '.agents/rules.md'),
  path.join(rootDir, '.agents/workflows.md'),
  path.join(rootDir, '.agents/coordination.md'),
];

let hasErrors = false;

filesToCheck.forEach((filePath) => {
  if (!fs.existsSync(filePath)) {
    console.error(`❌ Target file to validate does not exist: ${filePath}`);
    hasErrors = true;
    return;
  }

  const content = fs.readFileSync(filePath, 'utf8');
  const dir = path.dirname(filePath);

  // Match [text](link)
  const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
  let match;
  while ((match = linkRegex.exec(content)) !== null) {
    const linkText = match[1];
    let linkUrl = match[2].trim();

    // Ignore web links and email links
    if (linkUrl.startsWith('http://') || linkUrl.startsWith('https://') || linkUrl.startsWith('mailto:')) {
      continue;
    }

    // Handle file:// urls (just in case)
    if (linkUrl.startsWith('file://')) {
      linkUrl = linkUrl.substring(7);
    }

    // Remove anchors/hashes
    const hashIndex = linkUrl.indexOf('#');
    const cleanUrl = hashIndex !== -1 ? linkUrl.substring(0, hashIndex) : linkUrl;

    if (!cleanUrl) {
      // It's just a local anchor link on the same page, e.g. [heading](#heading)
      continue;
    }

    // Resolve the path relative to the file containing the link
    const resolvedPath = path.resolve(dir, cleanUrl);

    // Verify existence
    if (!fs.existsSync(resolvedPath)) {
      console.error(`❌ Broken link in ${path.relative(rootDir, filePath)}: [${linkText}](${linkUrl})`);
      console.error(`   Resolved path does not exist: ${path.relative(rootDir, resolvedPath)}`);
      hasErrors = true;
    }
  }
});

if (hasErrors) {
  console.log('\n❌ Link validation failed.');
  process.exit(1);
} else {
  console.log('✅ All markdown links are valid.');
  process.exit(0);
}
