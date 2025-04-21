from odoo import api, fields, models


class Label(models.Model):
    _name = "please_test.label"
    _description = "Test Label"

    name = fields.Char("Label Name", required=True)
    description = fields.Text("Description")
    create_date = fields.Datetime(
        "Creation Date", default=fields.Datetime.now, readonly=True
    )

    def create_new_label(self):
        """Action to create a new label when button is clicked"""
        self.ensure_one()
        return self.env["please_test.label"].create(
            {
                "name": f"New Label from {self.name}",
                "description": f"Created from button click on {self.name}",
            }
        )
