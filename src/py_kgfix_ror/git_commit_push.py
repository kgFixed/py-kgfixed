import os
import subprocess
import shutil
from pathlib import Path

# function to push existing TTL files to a GitHub repository
def git_push_existing_ttl(repo_dir: Path, target_dir: str, version_name: str, tag_version= str | None) -> bool:
    try:
        repo_path = Path(repo_dir).absolute()
        target_path = (repo_path.parent / target_dir).absolute()
        print("repo_path", repo_path)
        print("target_path", target_path)
        
        if not target_path.exists():
            raise FileNotFoundError(f"ERROR: Folder {target_path} not found")
        
        ttl_files = [f for f in target_path.glob('*.ttl') if f.is_file()]
        if not ttl_files:
            raise FileNotFoundError(f"ERROR: No .ttl file in {target_path}")

        print(f"\n=== Processing {len(ttl_files)} files ===")

        tag_name = tag_version if tag_version else version_name.replace(' ', '-')
        
        tag_exists = subprocess.run(
            ['git', 'show-ref', '--tags', f'refs/tags/{tag_name}'],
            cwd=str(repo_path),
            capture_output=True
        ).returncode == 0

        if tag_exists:
            subprocess.run(
                ['git', 'tag', '-d', tag_name],
                cwd=str(repo_path),
                check=True
            )
            print(f"✓ Existing tag {tag_name} deleted")
    
        batch_file = repo_path / "git_operations.bat"
        print("target", target_path)
        try:
            with open(batch_file, 'w', encoding='utf-8') as f:
                f.write("@echo off\n")
                f.write(f"cd {repo_path.parent}/temp/ror-records\n")
                f.write("git pull origin kgfix_ror\n")
                
                f.write(f'xcopy "{target_path}\\*" ".\\{version_name}\\" /I /Y\n')
                
                f.write("git add .\n")
                f.write(f'git commit -m "[RDF] {version_name}"\n')
                f.write(f'git tag -d {tag_name} 2>nul\n')
                f.write(f'git push --delete origin {tag_name} 2>nul\n')
                f.write(f'git tag -a {tag_name} -m "Version {tag_name}"\n')
                f.write(f"git push origin kgfix_ror {tag_name}\n")
                
                f.write("cd ../..\n")
                f.write(f'echo ✅ TTLs pushed DIRECTLY to generated_ttl for {version_name}\n')

            subprocess.run(
                ['cmd', '/c', str(batch_file)],
                cwd=str(repo_path),
                shell=True,
                check=True
            )

            print(f"\n✅ Success: {len(ttl_files)} files pushed with tag {tag_name}")

            try:
                shutil.rmtree(target_path, ignore_errors=True)
                print(f"✓ Cleaned {target_dir} folder")
            except Exception as e:
                print(f"⚠️ Cleaning error: {str(e)}")

            return True

        finally:
            if batch_file.exists():
                os.remove(batch_file)

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Git error (code{e.returncode}): {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR : {str(e)}")
        return False
    
    