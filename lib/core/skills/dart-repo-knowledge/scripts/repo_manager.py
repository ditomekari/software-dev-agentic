import os

class RepoManager:
    def __init__(self, repo_dir: str) -> None:
        if not os.path.exists(repo_dir) or not os.path.isdir(repo_dir):
            raise ValueError(f"Repository directory '{repo_dir}' does not exist or is not a directory")
        
        self.repo_dir = repo_dir

        # Check if the repository directory is empty
        if len(os.listdir(self.repo_dir)) == 0:
            os.chdir(self.repo_dir)
            os.system("git submodule init")
            os.system("git submodule update")

        self.fetch()
        self.checkout("develop", force=True)

    def fetch(self) -> None:
        """
        Fetch the latest changes from the remote repository.
        This method updates the local repository with the latest changes from the remote.
        """
        os.chdir(self.repo_dir)
        os.system("git fetch")

    def checkout(self, target_branch: str, force: bool=True) -> None:
        """
        Checkout to the target branch.
        Args:
            target_branch (str): The name of the branch to checkout to.
            force (bool, optional): Whether to force the checkout operation. 
                                   If True, adds the "-f" option to git checkout.
                                   Defaults to True.
        """
        os.chdir(self.repo_dir)
        force_option = "-f" if force else ""
        os.system(f"git checkout {force_option} {target_branch}")
    
    def switch(self, target_branch, force: bool=True) -> None:
        """
        Switches to the target branch.
        Args:
            target_branch (str): The name of the branch to checkout to.
            force (bool, optional): Whether to force the checkout operation. 
                                   If True, adds the "-f" option to git checkout.
                                   Defaults to True.
        """
        
        os.chdir(self.repo_dir)
        force_option = "-f" if force else ""
        os.system(f"git switch {force_option} {target_branch}")

    def get_changelog(self) -> str:
        """
        Read and return the contents of the CHANGELOG.md file from the repository.
        Returns:
            str: The contents of the CHANGELOG.md file, or an empty string if the file doesn't exist.
        """
        changelog_path = os.path.join(self.repo_dir, "CHANGELOG.md")
        if os.path.exists(changelog_path):
            with open(changelog_path, 'r', encoding='utf-8') as file:
                return file.read()
        return ""

if __name__ == "__main__":
    mekari_pixel = RepoManager(os.path.join(os.path.dirname(__file__), "../mekari-pixel"))
    mekari_pixel.checkout("v1.39.0", force=True)