@echo off
echo Loading environment variables from .env...
for /f "tokens=1,* delims==" %%a in (.env) do (
    set %%a=%%b
)

@REM echo Confirming deployment for image: %GCR_IMAGE_NAME%
@REM set /p CONFIRM="Proceed with build, push, and deploy? (y/n): "
@REM if /i "%CONFIRM%" NEQ "y" (
@REM     echo Deployment cancelled.
@REM     exit /b
@REM )

@REM echo Syncing custom_addons to GCS bucket: %CUSTOM_MODULES_BUCKET%
@REM gsutil -m rsync -r custom_addons gs://%CUSTOM_MODULES_BUCKET%
@REM if %errorlevel% neq 0 (
@REM     echo Failed to sync custom modules. Exiting.
@REM     exit /b 1
@REM )

echo Building Docker image: %GCR_IMAGE_NAME%...
docker build -t %GCR_IMAGE_NAME% .
if %errorlevel% neq 0 (
    echo Docker build failed. Exiting.
    exit /b 1
)

echo Pushing image to Artifact Registry...
docker push %GCR_IMAGE_NAME%
if %errorlevel% neq 0 (
    echo Docker push failed. Exiting.
    exit /b 1
)

echo Deploying to Google Cloud Run...
gcloud run deploy %IMAGE_NAME% ^
    --image %GCR_IMAGE_NAME% ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --port %PORT% ^
    --add-cloudsql-instances=%CLOUDSQL_INSTANCE% ^
    --set-env-vars="DB_HOST=%DB_HOST%,DB_PORT=%DB_PORT%,DB_USER=%DB_USER%,DB_PASSWORD=%DB_PASSWORD%,CUSTOM_MODULES_BUCKET=%CUSTOM_MODULES_BUCKET%,FILESTORE_BUCKET=%FILESTORE_BUCKET%" ^
    --memory=2Gi ^
    --cpu=2
