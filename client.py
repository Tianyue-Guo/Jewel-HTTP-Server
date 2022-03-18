
import http.client


if __name__ == "__main__":
    conn = http.client.HTTPSConnection('127.0.0.1', 1010)
    conn.request("GET", "/")
    r1 = conn.getresponse()
    print(r1.status, r1.reason)
    data1 = r1.read()
    print(data1)