import re
from validators import validator, utils

ip_middle_octet = u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
ip_last_octet = u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"

regex = re.compile(
	# protocol identifier
	u"(?:(?:https?|ftp)://)"
	# user:pass authentication
	u"(?:\S+(?::\S*)?@)?"
	u"(?:cdn)"
	u"(?:"
	u"(?P<private_ip>"
	# IP address exclusion
	# private & local networks
	u"(?:(?:10|127)" + ip_middle_octet + u"{2}" + ip_last_octet + u")|"
	u"(?:(?:169\.254|192\.168)" + ip_middle_octet + ip_last_octet + u")|"
	u"(?:172\.(?:1[6-9]|2\d|3[0-1])" + ip_middle_octet + ip_last_octet + u"))"
	u"|"
	# IP address dotted notation octets
	# excludes loopback network 0.0.0.0
	# excludes reserved space >= 224.0.0.0
	# excludes network & broadcast addresses
	# (first & last IP address of each class)
	u"(?P<public_ip>"
	u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
	u"" + ip_middle_octet + u"{2}"
	u"" + ip_last_octet + u")"
	u"|"
	# host name
	u"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
	# domain name
	u"(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
	# TLD identifier
	u"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
	u")"
	# port number
	u"(?::\d{2,5})?"
	# resource path
	u"(?:/\S*)?"
	# query string
	u"(?:\?\S*)?",
	re.UNICODE | re.IGNORECASE
)

pattern = re.compile(regex)


@validator
def url(value, public=False):
	"""
	Return whether or not given value is a valid URL.

	If the value is valid URL this function returns ``True``, otherwise
	:class:`~validators.utils.ValidationFailure`.

	This validator is based on the wonderful `URL validator of dperini`_.

	.. _URL validator of dperini:
		https://gist.github.com/dperini/729294

	This is edited from the original `validators` library. 
	Instead of using `regex.match()`, it uses `regex.search()`.

	:param value: URL address string to validate
	:param public: (default=False) Set True to only allow a public IP address
	"""
	result = pattern.search(value)
	if not public:
		return result

	return result and not result.groupdict()['private_ip']