# Database credentials
$dbHost = "localhost"
$dbPort = "5432"
$dbUser = "postgres"   # Replace with your PostgreSQL username
$dbPassword = "postgres"  # Replace with your PostgreSQL password
$dbName = "beers"

# Paths
$createSqlPath = "create.sql"  # Replace with the path to your create.sql file
$dataFolderPath = "data"  # Replace with the path to your data folder

# Set environment variable for psql password
$env:PGPASSWORD = $dbPassword

# Create the database
psql -h $dbHost -p $dbPort -U $dbUser -c "CREATE DATABASE $dbName;"

# Create the schema
psql -h $dbHost -p $dbPort -U $dbUser -d $dbName -f $createSqlPath

# Insert data from .dat files
Get-ChildItem -Path $dataFolderPath -Filter *.dat | ForEach-Object {
    $filePath = $_.FullName
    $tableName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
    psql -h $dbHost -p $dbPort -U $dbUser -d $dbName -c "\COPY $tableName FROM '$filePath' WITH (FORMAT csv, HEADER false, DELIMITER ',');"
}

# Remove environment variable
Remove-Item Env:PGPASSWORD