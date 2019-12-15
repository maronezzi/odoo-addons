from odoo import models, api, fields
import re

class WhatsappSendMessage(models.TransientModel):

    _name = 'whatsapp.message.wizard'
    _description = "WhatsApp"


    user_id = fields.Many2one('res.partner', string="Recipient")
    mobile = fields.Char(related='user_id.mobile', required=True)
    message = fields.Text(string="message", required=True)

    def send_message(self):
        if self.message and self.mobile:
            message_string = ''
            message = self.message.split(' ')
            for msg in message:
                message_string = message_string + msg + '%20'
            message_string = message_string[:(len(message_string) - 3)]
            print("+55" + re.sub(r"\D", "", self.mobile))
            return {
                'type': 'ir.actions.act_url',
                'url': "https://api.whatsapp.com/send?phone=550" + re.sub(r"\D", "", self.mobile)+"&text=" + message_string,
                'target': 'self',
                'res_id': self.id,
            }