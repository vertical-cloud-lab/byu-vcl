function FindProxyForURL(url, host) {
  // Chrome's own update/model/safe-browsing traffic doesn't need the Pi's IP,
  // and on a fresh profile it is tens of MB -- keep it off the tunnel.
  var direct = [".gvt1.com", ".gvt2.com", "update.googleapis.com", "clients2.google.com",
                "clients2.googleusercontent.com", "optimizationguide-pa.googleapis.com",
                "safebrowsing.googleapis.com", "clientservices.googleapis.com",
                "content-autofill.googleapis.com", "android.clients.google.com"];
  for (var i = 0; i < direct.length; i++)
    if (dnsDomainIs(host, direct[i]) || host == direct[i].replace(/^\./, "")) return "DIRECT";
  return "SOCKS5 127.0.0.1:1080";
}
