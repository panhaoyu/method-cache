import subprocess


def run_command(command):
    """运行命令并处理错误"""
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def process_release(version_type="patch"):
    """处理版本更新、发布、提交和推送的核心逻辑"""
    print(f"Updating project version ({version_type})...")
    run_command(f"poetry version {version_type}")

    version = run_command("poetry version -s")
    print(f"New version: {version}")

    print("Publishing to Python package index...")
    run_command("poetry publish --build")

    print("Adding changes to git...")
    run_command("git add .")

    print(f"Committing changes with message: Release version {version}")
    run_command(f'git commit -m "Release version {version}"')

    print("Pushing changes to remote repository...")
    run_command("git push origin main")

    print("All steps completed successfully.")


def main():
    # 提示用户输入版本类型
    version_type = input("Enter version type (patch/minor/major), default is patch: ").strip()

    # 如果用户输入为空，默认使用 'patch'
    if not version_type:
        version_type = "patch"

    try:
        process_release(version_type)  # 调用处理函数，并传入版本类型
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing command: {e.cmd}")
        print(f"Error message: {e.stderr}")
        print("Terminating script due to error.")
        exit(1)


if __name__ == "__main__":
    main()
