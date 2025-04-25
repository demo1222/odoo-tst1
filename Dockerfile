FROM odoo:16.0

USER root

RUN apt-get update && \
    apt-get install -y curl apt-transport-https ca-certificates gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && \
    apt-get install -y google-cloud-sdk

# Create directory for custom addons and filestore with proper permissions
RUN mkdir -p /var/lib/odoo/custom_addons && \
    mkdir -p /var/lib/odoo/filestore && \
    mkdir -p /var/lib/odoo/data && \
    chown -R odoo:odoo /var/lib/odoo

# Copy odoo configuration file
COPY odoo.conf /etc/odoo/odoo.conf
RUN chown odoo:odoo /etc/odoo/odoo.conf

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    sed -i 's/\r$//' /entrypoint.sh

USER odoo

EXPOSE 8080

# Start Odoo using the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
CMD exec odoo --db_host=$DB_HOST --db_user=$DB_USER --db_password=$DB_PASSWORD --http-port=8080 --http-interface=0.0.0.0
