IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'fastapi_demo')
BEGIN
    CREATE DATABASE fastapi_demo;
END
GO
