@REM @echo off

echo Loading environment variables from .env...
for /f "tokens=1,2 delims==" %%a in (.env) do (
    set %%a=%%b
)
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
