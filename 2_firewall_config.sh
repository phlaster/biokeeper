sudo ufw status

ufw default deny incoming

ufw default allow outgoing
ufw allow ssh # or 22
ufw allow 1337

sudo ufw enable

# sudo ufw disable

# sudo ufw status numbered

# sudo ufw delete 1 #or any number

# sudo ufw allow http # or 80
# sudo ufw allow https # or 443
