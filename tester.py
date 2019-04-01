import random, string


def get_test_address_prefix():
    x = ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase +
                      string.digits) for _ in range(5))
    return 'test-{}'.format(x)


def test_spammyness(server, sender, msg):
    try:
        to_prefix = get_test_address_prefix()
        to = '{}@mail-tester.com'.format(to_prefix)
        del msg['To']
        msg['To'] = to
        server.sendmail(sender, to, msg.as_string())
        url = 'https://www.mail-tester.com/{}'.format(to_prefix)
        return url
    except Exception, e:
        raise
        raise Exception("Unable to run email sanity tester\n\t{}".format(e))
