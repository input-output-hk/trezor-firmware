#!/usr/bin/env python
import sys
from collections import defaultdict

from messages_pb2 import (
    MessageType,
    wire_bootloader,
    wire_debug_in,
    wire_debug_out,
    wire_in,
    wire_no_fsm,
    wire_out,
)

fh = open("messages_map.h", "wt")
fl = open("messages_map_limits.h", "wt")

# len("MessageType_MessageType_") - len("_fields") == 17
TEMPLATE = "\t{{ {type} {dir} {msg_id:46} {fields:29} {process_func} }},\n"

LABELS = {
    wire_in: "in messages",
    wire_out: "out messages",
    wire_debug_in: "debug in messages",
    wire_debug_out: "debug out messages",
}


def handle_message(fh, fl, skipped, message, extension):
    name = message.name
    short_name = name.split("MessageType_", 1).pop()
    assert short_name != name

    for s in skipped:
        if short_name.startswith(s):
            return

    interface = "d" if extension in (wire_debug_in, wire_debug_out) else "n"
    direction = "i" if extension in (wire_in, wire_debug_in) else "o"

    options = message.GetOptions()
    bootloader = options.Extensions[wire_bootloader]
    no_fsm = options.Extensions[wire_no_fsm]

    if getattr(options, "deprecated", None):
        fh.write("\t// Message %s is deprecated\n" % short_name)
        return
    if bootloader:
        fh.write("\t// Message %s is used in bootloader mode only\n" % short_name)
        return
    if no_fsm:
        fh.write("\t// Message %s is not used in FSM\n" % short_name)
        return

    if direction == "i":
        process_func = "(void (*)(const void *))fsm_msg%s" % short_name
    else:
        process_func = "0"

    fh.write(
        TEMPLATE.format(
            type="'%c'," % interface,
            dir="'%c'," % direction,
            msg_id="MessageType_%s," % name,
            fields="%s_fields," % short_name,
            process_func=process_func,
        )
    )

    bufsize = None
    t = interface + direction
    if t == "ni":
        bufsize = "MSG_IN_SIZE"
    elif t == "no":
        bufsize = "MSG_OUT_SIZE"
    elif t == "do":
        bufsize = "MSG_DEBUG_OUT_SIZE"
    if bufsize:
        fl.write(
            '_Static_assert(%s >= sizeof(%s), "msg buffer too small");\n'
            % (bufsize, short_name)
        )


skipped = sys.argv[1:]

fh.write(
    "\t// This file is automatically generated by messages_map.py -- DO NOT EDIT!\n"
)
fl.write(
    "// This file is automatically generated by messages_map.py -- DO NOT EDIT!\n\n"
)

messages = defaultdict(list)

for message in MessageType.DESCRIPTOR.values:
    extensions = message.GetOptions().Extensions

    for extension in (wire_in, wire_out, wire_debug_in, wire_debug_out):
        if extensions[extension]:
            messages[extension].append(message)

for extension in (wire_in, wire_out, wire_debug_in, wire_debug_out):
    if extension == wire_debug_in:
        fh.write("\n#if DEBUG_LINK\n")
        fl.write("\n#if DEBUG_LINK\n")

    fh.write("\n\t// {label}\n\n".format(label=LABELS[extension]))

    for message in messages[extension]:
        handle_message(fh, fl, skipped, message, extension)

    if extension == wire_debug_out:
        fh.write("\n#endif\n")
        fl.write("#endif\n")

fh.close()
fl.close()
