# Python Script that handles GET, POST and PUT requests to an ElasticSearch domain. It passes request parameters in the body (payload) of the request and the Signed SigV4 Authentication information is passed in an Authorization header. 

# Import required libraries
import sys, os, base64, datetime, hashlib, hmac, urllib, requests, json

# Read AWS access key from env. variables or configuration file. Best practice is NOT
# to embed credentials in code
access_key = os.environ.get('AWS_ACCESS_KEY')
secret_key = os.environ.get('AWS_SECRET_KEY')
if access_key is None or secret_key is None:
    print 'No access key is available.'
    sys.exit()

# Read Command Parameters, show usage information if not supplied
if len(sys.argv) < 5:
    print 'Error: Missing Parameters. Usage: '
    print 'python sigv4ElasticSearchClient.py <ES Endpoint> <AWS Region> <ES URL> <HTTP Method> <Query Data>'
    print ''
    print '    <ES Endpoint> - REQUIRED - domain-specific endpoint for accessing the search API, e.g. http://search-domainname-domainid.us-east-1.aes.amazonaws.com'
    print '    <AWS Region>  - REQUIRED - For a list of supported regions, see http://docs.aws.amazon.com/general/latest/gr/rande.html#elasticsearch-service-regions'
    print '    <ES URL>      - REQUIRED - ES API URL, See Elasticsearch Documentation https://www.elastic.co/guide/index.html'
    print '    <HTTP Method> - REQUIRED - ES API HTTP Method, e.g. GET, POST, PUT'
    print '    <Query Data>  - OPTIONAL - ES API HTTP Request Data'
    print ''
    print 'Test Access and Connectivity example: '
    print 'python sigv4ElasticSearchClient.py search-mydomain-abc5vcipeeuvp4jg45k7abcdef.us-east-1.es.amazonaws.com us-east-1 /_cluster/health GET'
    print 'Perform a Search example: '
    print 'python sigv4ElasticSearchClient.py search-mydomain-abc5vcipeeuvp4jg45k7abcdef.us-east-1.es.amazonaws.com us-east-1 /_search POST \'{"query": { "query_string": { "query": "mysearchterm" }}}\''
    print 'Index a document example: '
    print 'python sigv4ElasticSearchClient.py search-mydomain-abc5vcipeeuvp4jg45k7abcdef.us-east-1.es.amazonaws.com us-east-1 /indexname/type/id PUT \'{"name": "John Doe"}\''
    sys.exit()
else:
    endpoint = sys.argv[1]
    region = sys.argv[2]
    canonical_uri = sys.argv[3]
    method = sys.argv[4]
    service = 'es'
    if method == 'GET':
        payload = ''
    else:
        payload = sys.argv[5]

# Key derivation functions.
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

# Create a date for headers and the credential string
t = datetime.datetime.utcnow()
amz_date = t.strftime('%Y%m%dT%H%M%SZ') # Format date as YYYYMMDD'T'HHMMSS'Z'
datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

# create a canonical request
# canonical_uri and request type already defined.

# create the canonical query string. In this example, request
# parameters are passed in the body of the request and the query string
# is blank.
canonical_querystring = ''

#Create the canonical headers
canonical_headers = 'host:' + endpoint + '\n'

#Create the list of signed headers
signed_headers = 'host'

#Create payload hash. In this example, the payload (body of the request) contains the request parameters.
payload_hash = hashlib.sha256(payload).hexdigest()

#Combine elements to create create canonical request
canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

#Create the string to sign
algorithm = 'AWS4-HMAC-SHA256'
credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request).hexdigest()

# Create the signing key using the function defined above.
signing_key = getSignatureKey(secret_key, datestamp, region, service)

# Sign the string_to_sign using the signing_key
signature = hmac.new(signing_key, (string_to_sign).encode("utf-8"), hashlib.sha256).hexdigest()

# Put the signature information in a header named Authorization.
authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
headers = {'X-Amz-Date':amz_date,
           'Authorization':authorization_header}

# Create a request url and issue a request
request_url = 'https://' + endpoint + canonical_uri

print '\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++'
print 'Request: ' + request_url
print headers
if method == 'GET':
    r = requests.get(request_url, data=payload, headers=headers)

if method == 'POST':
    r = requests.post(request_url, data=payload, headers=headers)

if method == 'PUT':
    r = requests.put(request_url, data=payload, headers=headers)

print '\nRESPONSE++++++++++++++++++++++++++++++++++++'
print 'Response code: %d\n' % r.status_code
print r.text
# end 
