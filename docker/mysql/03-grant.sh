#!/bin/bash
set -e

# Connect via Unix socket to the temporary server
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<EOF
GRANT ALL PRIVILEGES ON dw.* TO '${MYSQL_USER}'@'%';
GRANT ALL PRIVILEGES ON meta.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
EOF