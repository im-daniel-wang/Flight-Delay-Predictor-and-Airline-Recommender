#export DATABASE_NAME=msia423_db

# -p ${MYSQL_PORT}:${MYSQL_PORT} \ 
# echo "sup"
# echo  ${MYSQL_HOST}

docker run -it \
--env MYSQL_HOST \
--env MYSQL_PORT \
--env MYSQL_USER \
--env MYSQL_PASSWORD \
--env DATABASE_NAME \
flight_db src/flight_db.py rds --truncate
