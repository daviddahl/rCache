import twisted.internet import reactor, defer
import hyperestraier


@defer.deferredGenerator
def testUpdateAndSearch()
    doc = hyperestraier.Document()
    doc.add_attr("@uri", "http://localhost/example.txt")
    doc.add_attr("@title", "Over the rainbow")
    doc.add_text("There's a land that I heard of once in a lullaby.")
    doc.add_text("Somewhere over the rainbow.  Way up high.")
    wfd = defer.waitForDeferred(node.put_doc(doc))
    yield wfd
    print wfd.getResult()

    cond = hyperestraier.Condition()
    cond.set_phrase("rainbow AND lullaby")
    wfd = defer.waitForDeferred(node.search(cond, 0))
    yield wfd
    nres = wfd.getResult()
    if nres:
        for rdoc in nres.docs:
            print "#" * 20
            v = rdoc.attr("@uri")
            print "URI: " + v
            v = rdoc.attr("@title")
            print "TITLE: " + v
            print rdoc.snippet

node = hyperestraier.Node(hyperestraier.AysnTransport())
node.set_url("http://localhost:1978/node/test")
node.set_auth("admin", "admin")

testUpdateAndSearch()
reactor.run() 
