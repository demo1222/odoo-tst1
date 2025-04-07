from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)


class ApiProduct(models.Model):
    _name = "api.product"
    _description = "API Product Data"
    _order = "priority desc, design_difficulty desc, name"  # Order by priority, then design priority, then name

    api_id = fields.Integer("API ID", required=True)
    name = fields.Char("Name", required=True)
    date = fields.Date("Date")
    design = fields.Char("Design")
    fast_ship = fields.Boolean("Fast Ship", default=False)
    quantity = fields.Integer("Quantity", default=1)
    email = fields.Char("Email")

    # New fields for additional data
    shirt_color = fields.Char("Shirt Color")
    size = fields.Char("Size")
    fit_type = fields.Char("Fit Type")
    design_placement = fields.Char("Design Placement")
    notes = fields.Text("Notes")
    photo_url = fields.Char("Photo URL")
    delivery_date = fields.Date("Delivery Date")
    address = fields.Char("Shipping Address")

    design_difficulty = fields.Selection(
        [
            ("0", "Standard"),
            ("1", "Quick Edit"),
            ("2", "Some Effort"),
            ("3", "Time-Consuming"),
            ("4", "Complex Design"),
            ("5", "Intensive Work"),
        ],
        help="Design difficulty level",
        default="0",
        string="Design difficulty",
        tracking=True,
    )

    # New state field with selection options
    state = fields.Selection(
        [
            ("all_products", "All Products"),
            ("processing", "Processing"),
            ("approving", "Approving"),
            ("done", "Done"),
        ],
        string="Status",
        default="all_products",
        tracking=True,
        readonly=False,
        group_expand="_read_group_state",
    )

    manual_urgent = fields.Boolean(string="Manual Urgent", default=False)

    # Add this method to properly expand groups in kanban
    @api.model
    def _read_group_state(self, states, domain, order):
        # Return all possible values for state field
        return [state[0] for state in self._fields["state"].selection]

    # Priority field for sorting (computed based on tags)
    priority = fields.Integer(
        string="Priority", compute="_compute_priority", store=True
    )

    @api.depends("fast_ship", "quantity", "design", "manual_urgent")
    def _compute_priority(self):
        for record in self:
            _logger.info(f"Computing priority for record: {record}")
            # Default priority = 0
            priority = 0

            # Priority 4: Manual Urgent
            if record.manual_urgent:
                priority += 100
            # Priority 3 highest: fast_ship
            if record.fast_ship:
                priority += 50
            # Priority 2: Bulk Order (quantity > 10)
            if record.quantity > 10:
                priority += 20
            # Priority 1: Custom design
            if record.design:
                priority += 10

            record.priority = priority

    @api.model
    def create(self, vals):
        # Set default state if not provided
        if "state" not in vals:
            vals["state"] = "all_products"
        return super(ApiProduct, self).create(vals)

    def toggle_manual_urgent(self):
        for record in self:
            record.manual_urgent = not record.manual_urgent
            # Force recompute priority when toggled directly
            record._compute_priority()
        return True

    @api.model
    def fetch_and_store_api_data(self):
        """Fetch data from local API and store it in the database"""
        try:
            # Try different hostnames for different environments

            hostname = "http://host.docker.internal:8000"

            response = None
            exception = None

            url = f"{hostname}/api/get_data"
            _logger.info(f"Trying to connect to API at: {url}")
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                _logger.info(f"Successfully connected to API at: {url}")

            if not response or response.status_code != 200:
                raise exception or ValueError("Could not connect to any API endpoint")

            # Parse JSON response
            api_data = response.json()
            _logger.info(f"API response data: {api_data}")

        except (requests.exceptions.RequestException, ValueError) as e:
            _logger.error(f"Could not connect to API: {str(e)}")
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "API Connection Error",
                    "message": f"Could not connect to API: {str(e)}",
                    "sticky": True,
                    "type": "danger",
                },
            }

        if api_data.get("status") == "success" and "data" in api_data:
            try:
                # Track how many products were added and updated
                added_count = 0
                updated_count = 0

                for product_data in api_data["data"]:
                    # Make sure we have a valid product name
                    product_name = product_data.get("product")
                    if not product_name:  # Add explicit check for empty product name
                        _logger.warning(
                            f"Skipping product with no name: {product_data}"
                        )
                        continue

                    try:
                        # Check if a product with the same API ID already exists
                        api_id = product_data.get("id")
                        existing_product = self.search(
                            [("api_id", "=", api_id)], limit=1
                        )

                        product_values = {
                            "api_id": api_id,
                            "name": product_name,
                            "date": product_data.get("date"),
                            "design": product_data.get("design", ""),
                            "fast_ship": product_data.get("fastShip") == "True",
                            "quantity": product_data.get("quantity", 1),
                            "email": product_data.get("mail", ""),
                            # Add new fields
                            "shirt_color": product_data.get("shirtColor", ""),
                            "size": product_data.get("size", ""),
                            "fit_type": product_data.get("fitType", ""),
                            "design_placement": product_data.get("designPlacement", ""),
                            "notes": product_data.get("notes", ""),
                            "photo_url": product_data.get("photoURL", ""),
                            "delivery_date": product_data.get("deliveryDate", False),
                            "address": product_data.get("address", ""),
                        }

                        if not existing_product:
                            # Create new product
                            api_product = self.create(product_values)
                            _logger.info(
                                f"Created API product: {api_product.name}, ID: {api_product.api_id}"
                            )
                            added_count += 1

                    except Exception as e:
                        _logger.error(f"Error processing API product: {e}")

                # Update success message to show counts
                message = f"API products imported successfully: {added_count} added, {updated_count} updated"
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "API Import",
                        "message": message,
                        "sticky": False,
                        "type": "success",
                    },
                }
            except Exception as e:
                _logger.error(f"Error in fetch_and_store_api_data: {e}", exc_info=True)
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "Error",
                        "message": f"Error processing API data: {str(e)}",
                        "sticky": False,
                        "type": "danger",
                    },
                }
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "API Error",
                    "message": f"Invalid response format from API: {api_data}",
                    "sticky": False,
                    "type": "danger",
                },
            }
