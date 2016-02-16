from unittest import TestCase
from decimal import Decimal
import base64

import eopayment.paybox as paybox
import eopayment

class PayboxTests(TestCase):
    def test_sign(self):
        key = '0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF'.decode('hex')
        d = dict(paybox.sign([
                    ['PBX_SITE', '1999888'],
                    ['PBX_RANG', '32'],
                    ['PBX_IDENTIFIANT', '110647233'],
                    ['PBX_TOTAL', '999'], 
                    ['PBX_DEVISE', '978'],
                    ['PBX_CMD', 'TEST Paybox'],
                    ['PBX_PORTEUR', 'test@paybox.com'],
                    ['PBX_RETOUR', 'Mt:M;Ref:R;Auto:A;Erreur:E'],
                    ['PBX_HASH', 'SHA512'],
                    ['PBX_TIME', '2015-06-08T16:21:16+02:00'],
                ],
                key))
        result = '7ABB5F7A31DF4C8976A44374D3BA2F9831E7927CFD62F774ED378F4E27471708F4EFE6D0BEFA44EBABCBD978B661C74E22EEB16DEF73A510E86D0A5C0E7B6D88'
        self.assertIn('PBX_HMAC', d)
        self.assertEqual(d['PBX_HMAC'], result)

    def test_request(self):
        key = '0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF'
        backend = eopayment.Payment('paybox', {
            'platform': 'test',
            'site': '12345678',
            'rang': '001',
            'identifiant': '12345678',
            'shared_secret': key,
            'callback': 'http://example.com/callback',
        })
        time = '2015-07-15T18:26:32+02:00'
        email = 'bdauvergne@entrouvert.com'
        transaction_id, kind, what = backend.request(
            Decimal('19.99'), email=email,
            transaction_id='1234', time=time)
        self.assertEqual(kind, eopayment.FORM)
        self.assertEqual(transaction_id, '1234')
        from xml.etree import ElementTree as ET
        root = ET.fromstring(str(what))
        self.assertEqual(root.tag, 'form')
        self.assertEqual(root.attrib['method'], 'POST')
        self.assertEqual(root.attrib['action'], paybox.URLS['test'])
        for node in root:
            self.assertIn(node.attrib['type'], ('hidden', 'submit'))
            if node.attrib['type'] == 'submit':
                self.assertEqual(set(node.attrib.keys()), set(['type', 'value']))
            if node.attrib['type'] == 'hidden':
                self.assertEqual(set(node.attrib.keys()), set(['type', 'name', 'value']))
                name = node.attrib['name']
                values = {
                    'PBX_RANG': '01',
                    'PBX_SITE': '12345678',
                    'PBX_IDENTIFIANT': '12345678',
                    'PBX_RETOUR': 'montant:M;reference:R;code_autorisation:A;erreur:E;signature:K',
                    'PBX_TIME': time,
                    'PBX_PORTEUR': email,
                    'PBX_CMD': '1234',
                    'PBX_TOTAL': '1999',
                    'PBX_DEVISE': '978',
                    'PBX_HASH': 'SHA512',
                    'PBX_HMAC': 'A0AA37FC3DD46F3233C0AD3BF95242CD71003D98F33DF85124E4423D53759A82A132EC2CC42B7234B22A75F00CF5DA124DF3A34331F3F6B9D7308B2EF09DCA3C',
                    'PBX_ARCHIVAGE': '1234',
                    'PBX_REPONDRE_A': 'http://example.com/callback',
                }
                self.assertIn(name, values)
                self.assertEqual(node.attrib['value'], values[name])

    def test_rsa_signature_validation(self):
        pkey = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDUgYufHuheMztK1LhQSG6xsOzb
UX4D2A/QcMvkEcRVXFx5tQqcE9/JnMqE41TF/ebn7jC/MBxxtPFkUN7+EZoeMN7x
OWzAMDm/xsCWRvvel4GGixgm3aQRUPyTrlm4Ksy32Ya0rNnEDMAvB3dxOn7cp8GR
ZdzrudBlevZXpr6iYwIDAQAB
-----END PUBLIC KEY-----'''
        data = 'coin\n'
        sig64 = '''VCt3sgT0ecacmDEWWNVXJ+jGmIPBMApK42tBJV0FlDjpllOGPy8MsAmLW4/QjTtx
z0Dkz0NjxvU+5WzQZh9Uuxr/egRCwV4NMRWqu0zaVVioeBvl4/5CWm4f4/1L9+0m
FBFKOZhgBJnkC+l6+XhT4aYWKaQ4ocmOMV92yjeXTE4='''
        self.assertTrue(paybox.verify(data, base64.b64decode(sig64), key=pkey))
