** Install Ansible with pipx. On Parrot 7.5+ (Debian 13) a system pip install fails with PEP 668 (externally-managed), and apt ships an older copy. **

# Instructions
* Start with Parrot HTB Edition
* Install Ansible with pipx:
  * `sudo apt install -y pipx`
  * `pipx install --include-deps ansible`
  * `pipx ensurepath` (then open a new shell)
  * `pipx inject ansible pipx` (the playbook's pipx tasks run via Ansible's own interpreter, which needs the pipx module)
* Clone and enter the repo (git clone)
* ansible-galaxy install -r requirements.yml
* Make sure we have a sudo token (sudo whoami) — or run the playbook with `-K`
* ansible-playbook main.yml

# Off-Video Changes
* Mate-Terminal Colors, I show how to configure it here (https://www.youtube.com/watch?v=2y68gluYTcc). I just did the steps in that video on my old VM to backup the color scheme, then copied it to this repo.
* Evil-Winrm/Certipy/SharpCollection/CME/Impacket, will make a video for these soon
* Updated BurpSuite Activation. Later versions of ansible would hang if a shell script started a process that didn't die. Put a timeout on the java process
