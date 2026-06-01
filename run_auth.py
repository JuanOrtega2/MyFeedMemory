import os
import sys

repo_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

if __name__ == "__main__":
    from myfeedmemory.cli.authorize_linkedin import main

    main(print_only=False)
