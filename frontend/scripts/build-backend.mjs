import { execSync } from 'child_process';
import { mkdirSync } from 'fs';
import { join } from 'path';

const backendDir = join(process.cwd(), '../backend');
const tauriBinDir = join(process.cwd(), 'src-tauri/binaries');

mkdirSync(tauriBinDir, { recursive: true });

const target =
    process.env.TAURI_ENV_TARGET_TRIPLE ||
    process.env.CARGO_BUILD_TARGET ||
    process.env.RUST_TARGET ||
    'x86_64-unknown-linux-gnu';

const isWindows = target.includes('windows');

const outName = `app-${target}${isWindows ? '.exe' : ''}`;

console.log(`Building backend for ${target}`);
console.log(`Output: ${outName}`);

execSync(
    `pyinstaller app.py --onefile --name ${outName} --distpath "${tauriBinDir}"`,
    { cwd: backendDir, stdio: 'inherit' }
);
