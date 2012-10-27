import struct
import urllib, urllib2, httplib
import base64

BLOCK_SIZE = 8

headers = { 
            'accept-language': 'en-us,en;q=0.5', 
            'dnt': '1', 'keep-alive': '115', 
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1', 
            'accept-charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
}

class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302

def parse_cookie(headers):
    cookies = {}
    for cookie in headers.getheaders('Set-Cookie'):
        name, value = (cookie.split("=", 1) + [""])[:2]
        cookies[name] = value.split(";")[0]
    return cookies

def cookie_dict_to_string(cookie):
    return ";".join([(k+"="+v) for k,v in cookie.items()])

def send_request(url, params = None, headers = {}, cookie = None):
    opener = urllib2.build_opener(NoRedirectHandler)
    
    if cookie is not None:
        headers['Cookie'] = cookie
    
    post_data = None
    if params is not None:
        if isinstance(params, dict):
            post_data = urllib.urlencode(params)
        else:
            post_data = params

    request = urllib2.Request(url, post_data, headers)
    response = opener.open(request, timeout = 10)
    data = response.read()
    return {'headers': response.headers, 'data':data}

def oracle(ctext):
    import base64
    try:
        params = {'ctext':base64.b64encode(ctext)}
        send_request("http://localhost:8888",params)
    except Exception,e:
        return False
    return True

def set_byte(str, pos, byte):
    return str[:pos] + byte + str[pos+1:]

orig_cipher = base64.b64decode('AAAAAAAAAABlZAMZQvtlk/uV9v3EnuBVPsMiIfkDwTQUOUV0hkT0sw==')
print "Start padding oracle attack"
block_count = len(orig_cipher) / BLOCK_SIZE

plain_text = ""

for _ in range(block_count-1):
    print "Decrypting block #%d" % (_+1)
    cipher = orig_cipher[:-BLOCK_SIZE*_ or len(orig_cipher)]
    inter_value = [0]*BLOCK_SIZE
    fake_cipher = cipher
    for x in range(1,BLOCK_SIZE+1):
        for b in range(256):
            fake_cipher = set_byte(fake_cipher, len(cipher) - BLOCK_SIZE -x, chr(b))
            if oracle(fake_cipher):
                inter_value[BLOCK_SIZE-x] = x ^ b
                break
        for i in range(1, x+1):
            fake_cipher = set_byte(fake_cipher, len(cipher) - BLOCK_SIZE -i, chr( (x+1) ^ inter_value[BLOCK_SIZE-i]))
      
    for i in range(1,9):
        print chr( inter_value[BLOCK_SIZE-i] ^ ord(cipher[len(cipher) - BLOCK_SIZE -i])),
        plain_text = chr( inter_value[BLOCK_SIZE-i] ^ ord(cipher[len(cipher) - BLOCK_SIZE -i])) + plain_text


print plain_text