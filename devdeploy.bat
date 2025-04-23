@REM @echo off



REM Automate Odoo Deployment to Google Cloud Run

REM Load environment variables from .env file
echo Loading environment variables from .env...
for /f "tokens=1,2 delims==" %%a in (.env) do (
    set %%a=%%b
)

@REM REM 1. Authenticate with Google Cloud (if needed)
@REM echo Authenticating with Google Cloud...
@REM @REM gcloud auth configure-docker

@REM REM 2. Build the Docker image for Cloud Run
@REM echo Building the Docker image...
@REM docker build --platform=linux/amd64 -t %IMAGE_NAME% .

@REM REM 3. Push the Docker image to Google Artifact Registry
@REM echo Pushing the Docker image to Google Cloud...
@REM docker push %IMAGE_NAME%

@REM REM 4. Deploy Odoo to Google Cloud Run
@REM echo Deploying Odoo to Cloud Run...
@REM gcloud run deploy %IMAGE_NAME% ^
@REM     --image=%IMAGE_NAME% ^
@REM     --platform=managed ^
@REM     --region=%REGION% ^
@REM     --allow-unauthenticated ^
@REM     --port %PORT% ^
@REM     --add-cloudsql-instances=%CLOUDSQL_INSTANCE% ^
@REM     --set-env-vars="DB_HOST=%DB_HOST%,DB_USER=%DB_USER%,DB_PASSWORD=%DB_PASSWORD%" ^
 

@REM REM 5. Get Cloud Run Service URL
@REM echo Fetching Cloud Run Service URL...
@REM FOR /F "tokens=*" %%g IN ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format "value(status.url)"') DO (SET SERVICE_URL=%%g)

@REM REM 6. Display the Cloud Run URL
@REM echo Odoo is deployed! Access it here: %SERVICE_URL%




@echo off

set IMAGE_NAME=odootest2
set GCR_IMAGE_NAME=europe-north2-docker.pkg.dev/bidmyautotest/odootest/%IMAGE_NAME%

set /p CONFIRM="Do you really want to build and push the Docker image to Google Cloud Run container? (y/n): "
if /i "%CONFIRM%"=="y" (
    echo Building the Docker image...
    @REM copy /Y .env.dev .env
    docker build -t %GCR_IMAGE_NAME% .
    if %errorlevel% equ 0 (
        echo Docker image built successfully.

        echo Pushing the Docker image to %GCR_IMAGE_NAME%...
        docker push %GCR_IMAGE_NAME%

        if %errorlevel% equ 0 (
                echo Deploying %IMAGE_NAME% to Google Cloud Run managed platform...
                gcloud run deploy %IMAGE_NAME% ^
                    --image %GCR_IMAGE_NAME% ^
                    --platform managed ^
                    --region us-central1 ^
                    --allow-unauthenticated ^
                    --port %PORT% ^
                    --add-cloudsql-instances=%CLOUDSQL_INSTANCE% ^
                    --set-env-vars="DB_HOST=%DB_HOST%,DB_USER=%DB_USER%,DB_PASSWORD=%DB_PASSWORD%" ^
        ) else (
            echo Docker push failed. Exiting.
            exit /b 1
        )
    ) else (
        echo Docker build failed. Exiting.
        exit /b 1
    )
) else (
    echo Build and push cancelled.
)
