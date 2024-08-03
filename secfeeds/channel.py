from dataclasses import asdict, dataclass
from typing import List
from xml.etree import ElementTree as ET

_NS = {"atom": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/"}


@dataclass
class Channel:
    id: str | None = None
    text: str | None = None
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    type: str | None = None
    xmlUrl: str | None = None
    htmlUrl: str | None = None
    linkSelfUrl: str | None = None
    lastBuildDate: str | None = None

    def __post_init__(self):
        if not self.text:
            self.text = self.title
        elif not self.title:
            self.title = self.text

    @classmethod
    def from_feed_xml(cls, txt: str, init_url: str | None = None):
        root: ET.Element = ET.fromstring(txt.strip())
        attrs = {"type": root.tag}

        if init_url:
            attrs["xmlUrl"] = init_url

        date_tags: List[str] = ["updated", "pubDate"]
        tags: List[str] = [n for n in cls.__annotations__]

        if root.tag.lower() == "rss":
            date_tags.append("dc:date")
            channel: ET.Element = root.find("channel")
        elif root.tag == "{http://www.w3.org/2005/Atom}feed":
            date_tags = [f"atom:{t}" for t in date_tags]
            tags = [f"atom:{t}" for t in tags]
            channel: ET.Element = root

        for tag in tags:
            res: str | None = channel.findtext(tag, namespaces=_NS)
            if res:
                attrs[tag.split(":")[-1]] = res

        for link in channel.findall("atom:link", namespaces=_NS):
            if link.get("rel") == "self":
                attrs["linkSelfUrl"] = link.get("href")
                attrs["type"] = link.get("type")
            elif link.get("rel") == "alternate":
                attrs["htmlUrl"] = link.get("href")

        if "htmlUrl" not in attrs:
            attrs["htmlUrl"] = channel.findtext("link", namespaces=_NS)

        if "lastBuildDate" not in attrs:
            for t in date_tags:
                date = channel.findtext(t, namespaces=_NS)
                if date:
                    break
            attrs["lastBuildDate"] = date

        return cls(**{k: v.strip() for k, v in attrs.items() if v is not None})

    @classmethod
    def from_outline(cls, txt: str):
        element: ET.Element = ET.fromstring(txt.strip())
        return cls(**element.attrib)

    def to_outline(self) -> ET.Element:
        attrs = {k: v for k, v in asdict(self).items() if v is not None}
        attrs.pop("lastBuildDate", None)
        o: ET.Element = ET.Element("outline", attrs)
        return o
