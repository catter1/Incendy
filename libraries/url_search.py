import re
from validators import validator

ip_middle_octet = r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
ip_last_octet = r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"

regex = re.compile(
	# protocol identifier
	r"(?:(?:https?|ftp)://)"
	# user:pass authentication
	r"(?:\S+(?::\S*)?@)?"
	r"(?:cdn)"
	r"(?:"
	r"(?P<private_ip>"
	# IP address exclusion
	# private & local networks
	r"(?:(?:10|127)" + ip_middle_octet + r"{2}" + ip_last_octet + r")|"
	r"(?:(?:169\.254|192\.168)" + ip_middle_octet + ip_last_octet + r")|"
	r"(?:172\.(?:1[6-9]|2\d|3[0-1])" + ip_middle_octet + ip_last_octet + r"))"
	r"|"
	# IP address dotted notation octets
	# excludes loopback network 0.0.0.0
	# excludes reserved space >= 224.0.0.0
	# excludes network & broadcast addresses
	# (first & last IP address of each class)
	r"(?P<public_ip>"
	r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
	r"" + ip_middle_octet + r"{2}"
	r"" + ip_last_octet + r")"
	r"|"
	# host name
	r"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
	# domain name
	r"(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
	# TLD identifier
	r"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
	r")"
	# port number
	r"(?::\d{2,5})?"
	# resource path
	r"(?:/\S*)?"
	# query string
	r"(?:\?\S*)?",
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