import os.path
import os
import random
import logging
import urllib
from datetime import date

__all__ = ['PaymentCommon', 'URL', 'HTML', 'RANDOM', 'RECEIVED', 'ACCEPTED',
           'PAID', 'ERROR']


RANDOM = random.SystemRandom()

URL = 1
HTML = 2
FORM = 3

RECEIVED = 1
ACCEPTED = 2
PAID = 3
DENIED = 4
CANCELED = 5
ERROR = 99


class PaymentResponse(object):
    '''Holds a generic view on the result of payment transaction response.

       result -- holds the declarative result of the transaction, does not use
       it to validate the payment in your backoffice, it's just for informing
       the user that all is well.
       test -- indicates if the transaction was a test
       signed -- holds whether the message was signed
       bank_data -- a dictionnary containing some data depending on the bank,
       you have to log it for audit purpose.
       return_content -- when handling a response in a callback endpoint, i.e.
       a response transmitted directly from the bank to the merchant website,
       you usually have to confirm good reception of the message by returning a
       properly formatted response, this is it.
       bank_status -- if result is False, it contains the reason
       order_id -- the id given by the merchant in the payment request
       transaction_id -- the id assigned by the bank to this transaction, it
       could be the one sent by the merchant in the request, but it is usually
       an identifier internal to the bank.
    '''

    def __init__(self, result=None, signed=None, bank_data=dict(),
            return_content=None, bank_status='', transaction_id='',
            order_id='', test=False):
        self.result = result
        self.signed = signed
        self.bank_data = bank_data
        self.return_content = return_content
        self.bank_status = bank_status
        self.transaction_id = transaction_id
        self.order_id = order_id
        self.test = test

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.__dict__)

    def is_received(self):
        return self.result == RECEIVED

    def is_accepted(self):
        return self.result == ACCEPTED

    def is_paid(self):
        return self.result == PAID

    def is_error(self):
        return self.result == ERROR


class PaymentCommon(object):
    PATH = '/tmp'
    BANK_ID = '__bank_id'

    def __init__(self, options):
        self.logger = logging.getLogger(self.__class__.__module__)
        self.logger.debug('initializing with options %s', options)
        for value in self.description['parameters']:
            key = value['name']
            if 'default' in value:
                setattr(self, key, options.get(key, None) or value['default'])
            else:
                setattr(self, key, options.get(key))

    def transaction_id(self, length, choices, *prefixes):
        while True:
            parts = [RANDOM.choice(choices) for x in range(length)]
            id = ''.join(parts)
            name = '%s_%s_%s' % (str(date.today()),
                                 '-'.join(prefixes), str(id))
            try:
                fd = os.open(os.path.join(self.PATH, name),
                             os.O_CREAT | os.O_EXCL)
            except:
                raise
            else:
                os.close(fd)
                return id

class Form(object):
    def __init__(self, url, method, fields):
        self.url = url
        self.method = method
        self.fields = fields

    def __repr__(self):
        s = '<form method="%s" action="%s">' % (self.method, self.url)
        for field in self.fields:
            s+= '<input type="%s" name="%s" value="%s">' % (
                urllib.quote(field['type']),
                urllib.quote(field['name']),
                urllib.quote(field['value']))
        s += '<input type="submit" name="Submit">'
        s += '</form>'
        return s
