#!/usr/bin/env python

import unittest

from pymud.colors import colors, nocolors

widgets = {
    'SINGLEBAR':"--------------------------------------------------------------------------------",
    'DOUBLEBAR':"================================================================================",
}

class TextFormatter(object):

    def formatMessage(self,message):
        message.dict.update(nocolors)
        message.dict.update(widgets)
        if hasattr(self, 'format' + message.type):
            fn = getattr(self, 'format' + message.type)
            return fn(message)
        return ""

    def formatyousay(self,message):
        return "{WHITE}You say {BLUE}'{message}'{CLEAR}".format(**message.dict)

    def formatsay(self,message):
        return "{WHITE}{name} says {BLUE}'{message}'{CLEAR}".format(**message.dict)

    def formatchat(self,message):
        return "{LIGHTCYAN}<{channel}>{LIGHTYELLOW}[{name}]:{LIGHTCYAN} {message}{CLEAR}".format(**message.dict)

    def formatchatjoin(self,message):
        return "{LIGHTCYAN}<{channel}> {name} joins the chat.{CLEAR}".format(**message.dict)

    def formatchatleave(self,message):
        return "{LIGHTCYAN}<{channel}> {name} leaves the chat.{CLEAR}".format(**message.dict)

    def formaterror(self,message):
        return "{RED}ERROR:{error}{CLEAR}".format(**message.dict)

    def formatexception(self,message):
        return "{RED}{error}{CLEAR}".format(**message.dict)

    def formatcreated(self,message):
        return "{RED}{name} created {article} {klass} {id}!{CLEAR}".format(**message.dict)

    def formatlook(self,message):
        return "You see {description}.".format(**message.dict)

    def formatheader(self,message):
        return "{LIGHTBLUE}{title}{CLEAR}".format(**message.dict)

    def formatvariables(self,message):
        variables = []
        for name,value in message.dict['variables'].iteritems():
            if not name: continue
            variables.append("{WHITE}{0} = {1}{CLEAR}".format(name,value,**message.dict))
        return "\n".join(variables)

    def formatscriptNames(self,message):
        scripts = []
        for name in message.dict['scripts'].keys():
            if not name: continue
            scripts.append("{WHITE}{0}{CLEAR}".format(name,**message.dict))
        return "\n".join(scripts)

    def formatscripts(self,message):
        scripts = []
        for name,script in message.dict['scripts'].iteritems():
            if not name: continue
            scripts.append("""\
{WHITE}{0}{CLEAR}
{YELLOW}{SINGLEBAR}{CLEAR}
{1}""".format(name,script,**message.dict))
        return "\n".join(scripts)

    def formattriggers(self,message):
        triggers = []
        for name,trigger in message.dict['triggers'].iteritems():
            if not name: continue
            triggers.append("""\
{WHITE}{0}{CLEAR}
{YELLOW}{SINGLEBAR}{CLEAR}
{1}""".format(name,trigger,**message.dict))
        return "\n".join(triggers)

    def formatexit(self,message):
        return "{name}".format(**message.dict)

    def formataction(self,message):
        return "You {description}.".format(**message.dict)

    def formatinvalidcommand(self,message):
        return "I do not know how to do {name}.".format(**message.dict)

    def formatnotice(self,message):
        return "{notice}".format(**message.dict)

    def formathelp(self,message):
        return """\
{WHITE}{name}{CLEAR}
{YELLOW}{SINGLEBAR}{CLEAR}
{help}
""".format(**message.dict)

    def formatcommands(self,message):
        commands = []
        for name in sorted(message.dict['commands'].keys()):
            function = message.dict['commands'][name]
            doc = function.__doc__
            if doc:
                doc = doc.partition('.')[0]
            if doc:
                doc = doc.strip()
            else:
                doc = ""
            commands.append("{MAGENTA}{0:20} {WHITE}{1}{CLEAR}".format(name,doc,**message.dict))
        title = "{WHITE}Commands\n{YELLOW}{SINGLEBAR}{CLEAR}\n".format(**message.dict)
        return title + "\n".join(commands)

    def formatmap(self,message):
        location = message.dict['location']
        zone = message.dict['zone']
        if location.id not in zone.coordinates: return ""
        (x,y,z) = zone.coordinates[location.id]
        map = ""
        for j in xrange(y-zone.mapDistance,y+zone.mapDistance):
            for i in xrange(x-zone.mapDistance,x+zone.mapDistance):
                if (i,j,z) in zone.rooms:
                    map += zone.rooms[i,j,z]().mapColor
                    map += zone.rooms[i,j,z]().mapCharacter
                else:
                    map += "{CLEAR} "
            map +="\n"
        map += "{CLEAR} "
        return map.format(**message.dict)

class ColorTextFormatter(TextFormatter):

    def formatMessage(self,message):
        message.dict.update(colors)
        message.dict.update(widgets)
        if hasattr(self, 'format' + message.type):
            fn = getattr(self, 'format' + message.type)
            return fn(message)
        else:
            return ""

class Test(unittest.TestCase):

    def test(self):
        from message import Message
        tf = TextFormatter()
        ctf = ColorTextFormatter()
        m = Message("say",message="hello",name="Ed",id="1")
        print tf.formatMessage(m)
        print ctf.formatMessage(m)

if __name__ == "__main__":
    unittest.main()
