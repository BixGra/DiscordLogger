echo "docker build . -t discordlogger"

docker build . -t discordlogger

echo "docker compose up -d --remove-orphans"

docker compose up -d --remove-orphans

echo "docker image prune -a"

docker system prune -a