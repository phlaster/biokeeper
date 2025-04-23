ufw status

ufw default deny incoming
ufw default allow outgoing

ufw allow ssh # or 22
ufw allow 1337

ufw enable
