'''
Dummy payment backend module for debugging
'''

from decimal import Decimal
import string
import urllib2
import urlparse

from common import PaymentCommon, URL

__all__ = [ 'Payment' ]


class Payment(PaymentCommon):
    def __init__(self, options):
        self.options = options

    def request(self, amount, email=None, next_url=None):
        transaction_id = self.transaction_id(6, string.digits, 'dummy')

        dest_url = 'http://perso.entrouvert.org/~fred/paiement/?return=%s&tid=%s&amount=%s' % (
                        urllib2.quote(next_url),
                        transaction_id,
                        str(Decimal(amount)*100))

        return (transaction_id, URL, dest_url)

    def response(self, query_string):
        form = urlparse.parse_qs(query_string)
        return (True, form.get('tid')[0], '', None)
