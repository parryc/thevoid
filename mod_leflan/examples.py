#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.preprocessors import Preprocessor
from markdown.util import etree
import re

# --EX--
# SOURCE
# TARGET // NOTE
# --ENDEX--


class ExamplesPreprocessor(Preprocessor):
    def run(self, lines):
        """
        Add a counter to each example, without requiring
        the user to add it themself.
        """
        new_lines = []
        counter = 1
        for line in lines:
            if line == "--EX--":
                line += "|" + str(counter)
                counter += 1
                new_lines.append(line)
            else:
                new_lines.append(line)
        return new_lines


class ExamplesProcessor(BlockProcessor):
    def test(self, parent, block):
        """
        Test if valid example.
        """
        HEADER = "--EX--"
        FOOTER = "--ENDEX--"
        rows = [row.strip() for row in block.split("\n")]
        return HEADER == rows[0][:6] and rows[-1] == FOOTER

    def run(self, parent, blocks):
        """ Parse a table block and build table. """
        block = blocks.pop(0).split("\n")
        header = block[0].strip()
        counter = header.split("|")[1]
        rows = block[1:-1]

        example = etree.SubElement(parent, "div")

        label = etree.SubElement(example, "label")
        label.set("for", "example-toggle-" + counter)
        example_header = etree.SubElement(label, "span")
        example_header.set("class", "example-header")
        example_header.text = "examples"

        checkbox = etree.SubElement(example, "input")
        checkbox.set("id", "example-toggle-" + counter)
        checkbox.set("type", "checkbox")

        example_block = etree.SubElement(example, "div")
        example_block.set("class", "example-block")
        ol = etree.SubElement(example_block, "ol")
        ol.set("class", "example-list")

        li = etree.SubElement(ol, "li")
        for idx, row in enumerate(rows):
            if idx % 2 == 0:
                source = etree.SubElement(li, "span")
                source.set("class", "example-source")
                source.text = row.strip()
                etree.SubElement(li, "br")

            if idx % 2 == 1:
                parts = row.split("//")
                target = etree.SubElement(li, "span")
                target.set("class", "example-target")
                target.text = parts[0].strip()
                if len(parts) > 1:
                    etree.SubElement(li, "br")
                    note = etree.SubElement(li, "span")
                    note.set("class", "example-note")
                    note.text = parts[1].strip()
                if idx + 1 != len(rows):
                    li = etree.SubElement(ol, "li")


class Examples(Extension):
    def extendMarkdown(self, md):
        # The normal table extension uses '<hashheader', so why not
        md.parser.blockprocessors.register(ExamplesProcessor(md.parser), "examples", 71)
        md.preprocessors.register(ExamplesPreprocessor(md), "examples", 16)


# Enabled string loading of extension
def makeExtension(**kwargs):
    return Examples(**kwargs)
