import { execSync } from 'child_process';
import { existsSync, mkdirSync } from 'fs';
import { join } from 'path';

const backendDir = join(process.cwd(), '../backend');
const distDir = join(process.cwd(), '../dist-backend');
const appName = 'app';

if (!existsSync(distDir)) {
  mkdirSync(distDir, { recursive: true });
}

console.log(`Building backend for target: generic 'app' name`);
console.log(`Output name: ${appName}`);
console.log(`Output path: ${distDir}`);

try {
  // Ensure we are in the backend directory for pyinstaller
  execSync(
    `pyinstaller app.py --onefile --name ${appName} --distpath "${distDir}"`,
    {
      cwd: backendDir,
      stdio: 'inherit',
    }
  );
  console.log('Backend build successful.');
} catch (error) {
  console.error('Failed to build backend:', error.message);
  process.exit(1);
}
