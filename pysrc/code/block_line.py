

class Block:
    ''' A block of lines in a markdown file. Blocks are
    defined with open and closing ```type. Where type
    is optional.
    '''

    def __init__(self, first):
        ''' Start a block.
        Params:
            first (MarkdownLine): the first line in the block
        '''
        self._lines = []
        self._type = first.text.strip()[3:].strip()

    def get_type(self):
        return self._type

    def add_line(self, line):
        self._lines.append(line)

    def get_lines(self):
        return self._lines

    def make_content(self, code_info, lines):

        if self.get_type() == 'html':
            return self._make_content_html()

        if self.get_type() == 'code':
            return self._make_content_code(code_info, lines)

        if self.get_type() == 'plain':
            return self._make_content_plain()

        if self.get_type() == '':
            return self._make_content_none()

        raise Exception('Unknown block type ' + self.get_type())

    def _make_content_plain(self):
        ret = '<pre class="block_plainCode">\n'
        for md in self._lines[1:-1]:
            ret += md.text + '\n'
        ret += '</pre>'
        return ret

    def _make_content_html(self):
        ret = ''
        for md in self._lines[1:-1]:
            ret += md.text + '\n'
        return ret

    def _make_content_none(self):
        ret = '<pre>\n'
        for md in self._lines[1:-1]:
            ret += md.text + '\n'
        ret += '</pre>'
        return ret

    def _make_content_code(self, code_info, lines):
        import code.process_code
        if not 'processed_code' in code_info:
            code.process_code.process_code(lines, code_info)

        ret = '<pre class="codePreStyle">'

        for line in self._lines[1:-1]:

            html_out = line.text

            if line.link_info:

                info = line.link_info

                dest_anchor = None

                if 'memory_table' in info:
                    # For example:
                    # {
                    #     'opcode_i': 35, 'opcode_j': 38,
                    #     'memory_table': <code.memory_table.MemoryTable object at 0x00000170B409F630>,
                    #     'memory_table_name': 'ram',
                    #     'memory_table_entry': {
                    #         'range': [136, 137],
                    #         'name': 'cursor',
                    #         'description':
                    #         'Screen cursor used by BASIC routines'
                    #     }
                    # }

                    #print('MEMORY TABLE')
                    # print(line.text)
                    # print(info)
                    pass

                elif 'target_line' in info:
                    # For example:
                    # {
                    #     'opcode_i': 34, 'opcode_j': 39,
                    #     'target_line': <code.code_line.CodeLine object at 0x0000021B58E5E668>,
                    #     'target_label': 'PrintRoomDescription'
                    # }
                    dest_anchor = '{:04X}'.format(info['target_line'].address)
                    opcode_i = info['opcode_i']
                    opcode_j = info['opcode_j']
                    target_label = line.text[opcode_i:opcode_j]
                    if 'target_label' in info:
                        target_label = info['target_label']
                    anch_class = 'addr_code'
                    anch_title = line.text[opcode_i:opcode_j]

                    # print('CODE TARGET', opcode_i, opcode_j,
                    #      target_label, dest_anchor)
                    # print(line.text)

                if dest_anchor:
                    anchstr = '<a title="{}" class="{}" href="#{}">{}</a>'.format(anch_title, anch_class,
                                                                                  dest_anchor, target_label)
                    html_out = (html_out[:opcode_i] +
                                anchstr + html_out[opcode_j:])
                    extra_len = len(target_label) - (opcode_j - opcode_i)
                    #print(target_label, opcode_i, opcode_j, extra_len)
                    if extra_len > 0:
                        i = html_out.find(';')
                        if i >= 0:
                            j = i
                            while extra_len > 0 and html_out[i - 1] == ' ':
                                i -= 1
                                extra_len -= 1
                            html_out = html_out[:i] + html_out[j:]

                # This is the target of a link. Give it an ID for navigation.
                # TODO think about moving this target up to the label before or even the section
                # header above where appropriate?
                if 'is_target' in line.link_info and line.link_info['is_target']:
                    html_out = '<span id="' + \
                        html_out[0:4] + '">' + html_out[0:4] + \
                        '</span>' + html_out[4:]

            ret = ret + html_out + '\n'

        ret = ret + '</pre>'

        # TODO references to RAM
        # TODO links in jumps
        # print(code_info['memory'])

        return ret
