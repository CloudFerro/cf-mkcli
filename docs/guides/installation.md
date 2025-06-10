# Installation
### Prerequisites
1. Python 3.12 or higher
2. [pipx](https://pipx.pypa.io/stable/#on-linux)

### Installation
mkcli can be installed using pipx. To install mkcli, run the following command:

```bash
pipx install git+https://github.com/CloudFerro/cf-mkcli.git
```
> [!NOTE]
> pipx will install mkcli in a default location, which is usually `/root/.local/bin`. Don't forget to add
> this directory to your `PATH` environment variable if it is not already included. You can do it
> by adding the following line to your shell configuration file (e.g., `~/.bashrc`, `~/.zshrc`):
> ```export PATH=$PATH:/root/.local/bin``` or use `pipx ensurepath` command to automatically add it.

Now you can run it just with:
```bash
mkcli
```
or
```bash
python -m mkcl
```
