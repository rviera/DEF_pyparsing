import pyparsing as pp
from collections import defaultdict
from multiprocessing import (Process, Manager, Event)
import json

class DefParser:
    #
    def __init__(self):
        self.mydict = lambda: defaultdict(self.mydict)
        self.ignore_nets = True
        self.ignore_nets_route = False
        # Each list is a new process. Careful with dependencies.
        # 'dbuPerMicron' must be executed bofore the other, but can be after 'design'
        self.sections_grp = [['design', 'dbuPerMicron', 'diearea'],
                             ['components'],
                             # ['pins'],
                             # ['specialnets'],
                            ]
        if not self.ignore_nets:
            self.sections_grp.append(['nets'])
        self.n_elems_sections_grp = sum([len(x) for x in self.sections_grp])
        self.events = [Event()]
        self.design = ''
        # self.def_file = ['example_1.def']
        self.def_files = ['example_2.def']  # larger file with ~350k lines


    #
    def run(self):
        for curr_def in self.def_files:
            ifile = open(curr_def,'r')
            file_string = ifile.read()
            ifile.close()
            self.parser_def(file_string)
        # exit()

    #
    def parser_def(self, file_string):
        manager = Manager()
        shared_dict = manager.dict()
        # is_nets_section, is_not_nets_section  = self.divide_def_file(self.def_file_design[0])
        jobs = []
        for sections in self.sections_grp:
            p = Process(target=self.parse_sections, args=(sections, file_string, shared_dict))
            jobs.append(p)
            p.start()

        # Wait for the workers to finish
        for job in jobs:
            job.join()

        for sections in self.sections_grp:
            for section in sections:
                getattr(self, 'handle_' + section)(shared_dict)

    # Spawn the processes from each group of self.sections_grp
    def parse_sections(self, sections, def_string, shared_dict):
        for section in sections:
            to_parse = getattr(self, 'parse_' + section)
            for t, s, e in to_parse().scanString(def_string):
                shared_dict.update(t.asDict())
                break

    # Parse the DESIGN section of a .DEF file
    def parse_design(self):
        EOL = pp.LineEnd().suppress()
        linebreak = pp.Suppress(";" + pp.LineEnd())
        identifier = pp.Word(pp.alphanums + '._“!<>/[]$#$%&‘*+,/:<=>?@[\]^_`{|}~')  # CONFLICT with '();'
        number = pp.pyparsing_common.number
        word = pp.Word(pp.alphas)
        LPAR = pp.Suppress('(')
        RPAR = pp.Suppress(')')
        ORIENT = (pp.Keyword('N')
                | pp.Keyword('S')
                | pp.Keyword('E')
                | pp.Keyword('W')
                | pp.Keyword('FN')
                | pp.Keyword('FS')
                | pp.Keyword('FE')
                | pp.Keyword('FW'))
        pt = LPAR + pp.OneOrMore(number | pp.Keyword('*')) + RPAR  # pair of x,y
        design_id  = pp.Keyword('DESIGN')
        design     = design_id + identifier('DESIGN') + linebreak
        self.events[0].set()  # event[0] (parse_dbuPerMicron) has priority
        return design

    # Parse the UNITS DISTANCE MICRONS section of a .DEF file
    def parse_dbuPerMicron(self):
        EOL = pp.LineEnd().suppress()
        linebreak = pp.Suppress(";" + pp.LineEnd())
        identifier = pp.Word(pp.alphanums + '._“!<>/[]$#$%&‘*+,/:<=>?@[\]^_`{|}~')  # CONFLICT with '();'
        number = pp.pyparsing_common.number
        word = pp.Word(pp.alphas)
        LPAR = pp.Suppress('(')
        RPAR = pp.Suppress(')')
        ORIENT = (pp.Keyword('N')
                | pp.Keyword('S')
                | pp.Keyword('E')
                | pp.Keyword('W')
                | pp.Keyword('FN')
                | pp.Keyword('FS')
                | pp.Keyword('FE')
                | pp.Keyword('FW'))
        pt = LPAR + pp.OneOrMore(number | pp.Keyword('*')) + RPAR  # pair of x,y
        self.events[0].wait()  # event[0] (parse_dbuPerMicron) has priority
        dbuPerMicron_id  = pp.Keyword('UNITS DISTANCE MICRONS')
        dbuPerMicron     = dbuPerMicron_id + number('dbuPerMicron') + linebreak

        return dbuPerMicron

    # Parse the DIEAREA section of a .DEF file
    def parse_diearea(self):
        EOL = pp.LineEnd().suppress()
        linebreak = pp.Suppress(";" + pp.LineEnd())
        identifier = pp.Word(pp.alphanums + '._“!<>/[]$#$%&‘*+,/:<=>?@[\]^_`{|}~')  # CONFLICT with '();'
        number = pp.pyparsing_common.number
        word = pp.Word(pp.alphas)
        LPAR = pp.Suppress('(')
        RPAR = pp.Suppress(')')
        ORIENT = (pp.Keyword('N')
                | pp.Keyword('S')
                | pp.Keyword('E')
                | pp.Keyword('W')
                | pp.Keyword('FN')
                | pp.Keyword('FS')
                | pp.Keyword('FE')
                | pp.Keyword('FW'))
        pt = LPAR + pp.OneOrMore(number | pp.Keyword('*')) + RPAR  # pair of x,y
        self.events[0].wait()  # event[0] (parse_dbuPerMicron) has priority
        diearea_id  = pp.Keyword('DIEAREA')
        diearea     = pp.Group(pp.Suppress(diearea_id)
                               + pp.OneOrMore(pt)
                               + linebreak
                              ).setResultsName('DIEAREA')

        return diearea

    # Parse the COMPONENTS section of a .DEF file
    def parse_components(self):
        EOL = pp.LineEnd().suppress()
        linebreak = pp.Suppress(";" + pp.LineEnd())
        identifier = pp.Word(pp.alphanums + '._“!<>/[]$#$%&‘*+,/:<=>?@[\]^_`{|}~')  # CONFLICT with '();'
        number = pp.pyparsing_common.number
        word = pp.Word(pp.alphas)
        LPAR = pp.Suppress('(')
        RPAR = pp.Suppress(')')
        ORIENT = (pp.Keyword('N')
                | pp.Keyword('S')
                | pp.Keyword('E')
                | pp.Keyword('W')
                | pp.Keyword('FN')
                | pp.Keyword('FS')
                | pp.Keyword('FE')
                | pp.Keyword('FW'))
        pt = LPAR + pp.OneOrMore(number | pp.Keyword('*')) + RPAR  # pair of x,y
        self.events[0].wait()  # Wait for event[0] to finish
        components_id = pp.Keyword('COMPONENTS')
        end_components_id = pp.Keyword("END COMPONENTS").suppress()
        begin_comp = pp.Suppress(pp.Keyword('-'))
        ws_comp = pp.Suppress(pp.Keyword('+'))  # parameter division in components

        # compName
        compName = (identifier('comp_name') + identifier('cell')
                   ).setResultsName('compName')

        # EEQMASTER
        EEQMASTER = (ws_comp
                     + identifier
                     + identifier('EEQMASTER')
                    )

        # SOURCE
        SOURCE = (ws_comp
                  + pp.Suppress(pp.Keyword('SOURCE'))
                  + identifier('source_type')
                 ).setResultsName('SOURCE')

        # PLACEMENT
        PLACEMENT_ids = (pp.Keyword('FIXED')
                         | pp.Keyword('COVER')
                         | pp.Keyword('PLACED')
                         | pp.Keyword('UNPLACED')
                        )
        PLACEMENT_coord = (LPAR
                           + number('placement_x')
                           + number('placement_y')
                           + RPAR
                          )
        PLACEMENT = (ws_comp
                     + PLACEMENT_ids
                     + pp.Optional(PLACEMENT_coord + ORIENT('orientation'))
                    ).setResultsName('PLACEMENT')

        # MASKSHIFT
        MASKSHIFT = (ws_comp
                     + pp.Suppress(pp.Keyword('MASKSHIFT'))
                     + number('shiftLayerMasks')
                    ).setResultsName('MASKSHIFT')

        # HALO
        HALO = (ws_comp
                + pp.Keyword('HALO')
                + pp.Optional(pp.Keyword('SOFT'))
                + number('haloL')
                + number('haloB')
                + number('haloR')
                + number('haloT')
               ).setResultsName('HALO')

        # ROUTEHALO
        ROUTEHALO = (ws_comp
                     + pp.Keyword('ROUTEHALO')
                     + number('rhaloDist')
                     + identifier('rhaloMinLayer')
                     + identifier('rhaloMaxLayer')
                    ).setResultsName('ROUTEHALO')

        # WEIGHT
        WEIGHT = (ws_comp
                  + pp.Keyword('WEIGHT')
                  + number('weight')
                 ).setResultsName('WEIGHT')

        # REGION
        REGION = (ws_comp
                  + pp.Keyword('REGION')
                  + identifier('region')
                 ).setResultsName('REGION')

        # PROPERTY
        PROPERTY = (ws_comp
                    + pp.Keyword('PROPERTY')
                    + identifier('propName')
                    + identifier('propVal')
                   ).setResultsName('PROPERTY')

        subcomponent = pp.Group(begin_comp
                                + compName
                                + pp.Optional(EEQMASTER)
                                + pp.Optional(SOURCE)
                                + pp.Optional(PLACEMENT)
                                + pp.Optional(MASKSHIFT)
                                + pp.Optional(HALO)
                                + pp.Optional(ROUTEHALO)
                                + pp.Optional(WEIGHT)
                                + pp.Optional(REGION)
                                + pp.ZeroOrMore(PROPERTY)
                                + linebreak
                               ).setResultsName('subcomponents', listAllMatches=True)

        components = pp.Group(pp.Suppress(components_id)
                                          + number('numComps')
                                          + linebreak
                                          + pp.OneOrMore(subcomponent)
                                          + pp.Suppress(end_components_id)
                             ).setResultsName('COMPONENTS')

        return components

    # Parse the PINS section of a .DEF file
    def parse_pins(self):
        EOL = pp.LineEnd().suppress()
        linebreak = pp.Suppress(";" + pp.LineEnd())
        identifier = pp.Word(pp.alphanums + '._“!<>/[]$#$%&‘*+,/:<=>?@[\]^_`{|}~')  # CONFLICT with '();'
        number = pp.pyparsing_common.number
        word = pp.Word(pp.alphas)
        LPAR = pp.Suppress('(')
        RPAR = pp.Suppress(')')
        ORIENT = (pp.Keyword('N')
                | pp.Keyword('S')
                | pp.Keyword('E')
                | pp.Keyword('W')
                | pp.Keyword('FN')
                | pp.Keyword('FS')
                | pp.Keyword('FE')
                | pp.Keyword('FW'))
        pt = LPAR + pp.OneOrMore(number | pp.Keyword('*')) + RPAR  # pair of x,y
        pins_id = pp.Keyword('PINS')
        end_pins_id = pp.Keyword("END PINS").suppress()
        begin_pin = pp.Keyword('-')
        ws_pin = pp.Suppress(pp.Keyword('+'))  # parameter division in pins

        # pinName
        pinName = (identifier('pin_name')
                   + ws_pin
                   + pp.Keyword('NET')
                   + identifier('netName')
                  )

        # SPECIAL
        SPECIAL = (ws_pin
                   + pp.Keyword('SPECIAL')('SPECIAL')
                  )

        # DIRECTION
        DIRECTION_ids = (pp.Keyword('INPUT')
                       | pp.Keyword('OUTPUT')
                       | pp.Keyword('INOUT')
                       | pp.Keyword('FEEDTHRU')
                        )

        DIRECTION = (ws_pin
                     + pp.Keyword('DIRECTION')
                     + pp.OneOrMore(DIRECTION_ids('DIRECTION'))
                    )

        # NETEXPR
        NETEXPR = pp.Group(ws_pin
                           + pp.Keyword('NETEXPR')
                           + pp.OneOrMore(word)('net_expr')
                          ).setResultsName('NETEXPR')

        # SUPPLYSENSITIVITY
        SUPPLYSENSITIVITY = pp.Group(ws_pin
                                     + pp.Keyword('SUPPLYSENSITIVITY')
                                     + identifier('supply_sensitivity')
                                    ).setResultsName('SUPPLYSENSITIVITY')

        # GROUNDSENSITIVITY
        GROUNDSENSITIVITY = pp.Group(ws_pin
                                     + pp.Keyword('GROUNDSENSITIVITY')
                                     + identifier('ground_sensitivity')
                                    ).setResultsName('GROUNDSENSITIVITY')

        # USE
        USE_ids = (pp.Keyword('SIGNAL')
                 | pp.Keyword('POWER')
                 | pp.Keyword('GROUND')
                 | pp.Keyword('CLOCK')
                 | pp.Keyword('TIEOFF')
                 | pp.Keyword('ANALOG')
                 | pp.Keyword('SCAN')
                 | pp.Keyword('RESET')
                  )

        USE = (ws_pin
               + pp.Keyword('USE')
               + pp.OneOrMore(USE_ids('USE'))
              )

        # Common element to be used in the following subsections
        LAYER_layerName = pp.Keyword('LAYER') + identifier('layerName')

        # ANTENNAPINPARTIALMETALAREA
        ANTENNAPINPARTIALMETALAREA = pp.Group(ws_pin
                                              + pp.Keyword('ANTENNAPINPARTIALMETALAREA')
                                              + number
                                              + pp.Optional(LAYER_layerName)
                                              ).setResultsName('ANTENNAPINPARTIALMETALAREA')

        # ANTENNAPINPARTIALMETALSIDEAREA
        ANTENNAPINPARTIALMETALSIDEAREA = pp.Group(ws_pin
                                                  + pp.Keyword('ANTENNAPINPARTIALMETALSIDEAREA')
                                                  + number
                                                  + pp.Optional(LAYER_layerName)
                                                  ).setResultsName('ANTENNAPINPARTIALMETALSIDEAREA')

        # ANTENNAPINPARTIALCUTAREA
        ANTENNAPINPARTIALCUTAREA = pp.Group(ws_pin
                                            + pp.Keyword('ANTENNAPINPARTIALCUTAREA')
                                            + number
                                            + pp.Optional(LAYER_layerName)
                                            ).setResultsName('ANTENNAPINPARTIALCUTAREA')

        # ANTENNAPINDIFFAREA
        ANTENNAPINDIFFAREA = pp.Group(ws_pin
                                      + pp.Keyword('ANTENNAPINDIFFAREA')
                                      + number
                                      + pp.Optional(LAYER_layerName)
                                      ).setResultsName('ANTENNAPINDIFFAREA')

        # ANTENNAMODEL
        ANTENNAMODEL_ids = (pp.Keyword('OXIDE1')
                          | pp.Keyword('OXIDE2')
                          | pp.Keyword('OXIDE3')
                          | pp.Keyword('OXIDE4')
                           )

        ANTENNAMODEL = pp.Group(ws_pin
                                + pp.Keyword('ANTENNAMODEL')
                                + ANTENNAMODEL_ids
                               ).setResultsName('ANTENNAMODEL')

        # ANTENNAPINGATEAREA
        ANTENNAPINGATEAREA = pp.Group(ws_pin
                                      + pp.Keyword('ANTENNAPINGATEAREA')
                                      + number
                                      + pp.Optional(LAYER_layerName)
                                      ).setResultsName('ANTENNAPINGATEAREA')

        # ANTENNAPINMAXAREACAR
        ANTENNAPINMAXAREACAR = pp.Group(ws_pin
                                        + pp.Keyword('ANTENNAPINMAXAREACAR')
                                        + number
                                        + LAYER_layerName
                                        ).setResultsName('ANTENNAPINMAXAREACAR')

        # ANTENNAPINMAXSIDEAREACAR
        ANTENNAPINMAXSIDEAREACAR = pp.Group(ws_pin
                                            + pp.Keyword('ANTENNAPINMAXSIDEAREACAR')
                                            + number
                                            + LAYER_layerName
                                            ).setResultsName('ANTENNAPINMAXSIDEAREACAR')

        # ANTENNAPINMAXCUTCAR
        ANTENNAPINMAXCUTCAR = pp.Group(ws_pin
                                       + pp.Keyword('ANTENNAPINMAXCUTCAR')
                                       + number
                                       + LAYER_layerName
                                       ).setResultsName('ANTENNAPINMAXCUTCAR')

        # PLACEMENT_PINS
        PORT = (ws_pin
                + pp.Keyword('PORT')('PORT')
               )

        MASK = pp.Group( pp.Suppress(pp.Keyword('MASK'))
                        + number('maskNum')
                       ).setResultsName('MASK')

        SPACING = pp.Group( pp.Suppress(pp.Keyword('SPACING'))
                           + number('minSpacing')
                          ).setResultsName('SPACING')

        DESIGNRULEWIDTH = pp.Group( pp.Suppress(pp.Keyword('DESIGNRULEWIDTH'))
                                   + number('effectiveWidth')
                                  ).setResultsName('DESIGNRULEWIDTH')

        LAYER = pp.Group(ws_pin
                         + pp.Suppress(pp.Keyword('LAYER'))
                         + identifier('layerName')
                         + pp.Optional(MASK)
                         + pp.Optional(SPACING | DESIGNRULEWIDTH)
                         + pp.OneOrMore(pp.Group(pt))('coord')
                        ).setResultsName('LAYER')

        POLYGON =  pp.Group(ws_pin
                            + pp.Suppress(pp.Keyword('POLYGON'))
                            + identifier('layerName')
                            + pp.Optional(MASK)
                            + pp.Optional(SPACING | DESIGNRULEWIDTH)
                            + pp.OneOrMore(pp.Group(pt))('coord')
                           ).setResultsName('POLYGON')

        VIA =  pp.Group(ws_pin
                        + pp.Suppress(pp.Keyword('VIA'))
                        + identifier('viaName')
                        + pp.Optional(MASK)
                        + pp.Group(pt)('coord')
                       ).setResultsName('VIA')

        COVER = pp.Group(ws_pin
                         + pp.Suppress(pp.Keyword('COVER'))
                         + pp.Group(pt)('coord')
                         + ORIENT('orient')
                        ).setResultsName('COVER')

        FIXED = pp.Group(ws_pin
                         + pp.Suppress( pp.Keyword('FIXED'))
                         + pp.Group(pt)('coord')
                         + ORIENT('orient')
                        ).setResultsName('FIXED')

        PLACED = pp.Group(ws_pin
                          + pp.Suppress(pp.Keyword('PLACED'))
                          + pp.Group(pt)('coord')
                          + ORIENT('orient')
                         ).setResultsName('PLACED')

        PLACEMENT_PINS = (PORT
                          | pp.Group(LAYER | POLYGON | VIA)
                          | pp.Group(COVER | FIXED | PLACED)
                         )

        pin = pp.Group(pp.Suppress(begin_pin)
                       + pinName
                       + pp.Optional(SPECIAL)
                       + pp.Optional(DIRECTION)
                       + pp.Optional(NETEXPR)
                       + pp.Optional(SUPPLYSENSITIVITY)
                       + pp.Optional(GROUNDSENSITIVITY)
                       + pp.Optional(USE)
                       + pp.ZeroOrMore(ANTENNAPINPARTIALMETALAREA)
                       + pp.ZeroOrMore(ANTENNAPINPARTIALMETALSIDEAREA)
                       + pp.ZeroOrMore(ANTENNAPINPARTIALCUTAREA)
                       + pp.ZeroOrMore(ANTENNAPINDIFFAREA)
                       + pp.ZeroOrMore(ANTENNAMODEL)
                       + pp.ZeroOrMore(ANTENNAPINGATEAREA)
                       + pp.ZeroOrMore(ANTENNAPINMAXAREACAR)
                       + pp.ZeroOrMore(ANTENNAPINMAXSIDEAREACAR)
                       + pp.ZeroOrMore(ANTENNAPINMAXCUTCAR)
                       + pp.ZeroOrMore(PLACEMENT_PINS)('PLACEMENT')
                       + linebreak
                      ).setResultsName('pin', listAllMatches=True)

        pins = pp.Group(pp.Suppress(pins_id) + number('numPins') + linebreak
                        + pp.OneOrMore(pin)
                        + pp.Suppress(end_pins_id)
                       ).setResultsName('PINS')

        return pins

    # Parse the NETS section of a .DEF file
    def parse_nets(self):
        EOL = pp.LineEnd().suppress()
        linebreak = pp.Suppress(";" + pp.LineEnd())
        identifier = pp.Word(pp.alphanums + '._“!<>/[]$#$%&‘*+,/:<=>?@[\]^_`{|}~')  # CONFLICT with '();'
        number = pp.pyparsing_common.number
        word = pp.Word(pp.alphas)
        LPAR = pp.Suppress('(')
        RPAR = pp.Suppress(')')
        ORIENT = (pp.Keyword('N')
                | pp.Keyword('S')
                | pp.Keyword('E')
                | pp.Keyword('W')
                | pp.Keyword('FN')
                | pp.Keyword('FS')
                | pp.Keyword('FE')
                | pp.Keyword('FW'))
        pt = LPAR + pp.OneOrMore(number | pp.Keyword('*')) + RPAR  # pair of x,y
        nets_id = pp.Keyword('NETS')
        end_nets_id = pp.Keyword("END NETS").suppress()
        begin_net = pp.Keyword('-')
        ws_net = pp.Suppress(pp.Keyword('+'))  # parameter division in NETS

        # netName
        netName_1 = pp.Group(LPAR
                             + identifier('compName')
                             + identifier('pinName')
                             + pp.Optional(ws_net
                                           + pp.Keyword('SYNTHESIZED')
                                          )('SYNTHESIZED')
                             + RPAR
                            ).setResultsName('netName')

        netName_2 = pp.Group(pp.Keyword('MUSTJOIN')
                             + LPAR
                             + identifier('compName')
                             + identifier('pinName')
                             + RPAR
                            ).setResultsName('MUSTJOIN')

        netName = (identifier('netName')
                   + pp.OneOrMore(netName_1 | netName_2)
                  ).setResultsName('netName')

        # SHIELDNET
        SHIELDNET = pp.Group(ws_net
                             + pp.Keyword('SHIELDNET')
                             + identifier('shieldNetName')
                            ).setResultsName('SHIELDNET')

        # VPIN
        VPIN_PLACEMENT_ids = (pp.Keyword('PLACED')
                              | pp.Keyword('FIXED')
                              | pp.Keyword('COVER')
                             )

        VPIN_PLACEMENT = (VPIN_PLACEMENT_ids('PLACEMENT')
                          + pp.Group(pt)('pt')
                          + pp.ZeroOrMore(word('orient'))
                         )

        VPIN_LAYER = pp.Keyword('LAYER') + identifier('layerName')

        VPIN = pp.Group(ws_net
                        + pp.Keyword('VPIN')
                        + identifier('vpinName')
                        + pp.Optional(VPIN_LAYER)
                        + pp.Group(pt)('pt1')
                        + pp.Group(pt)('pt2')
                        + pp.Optional(pp.Group(VPIN_PLACEMENT)('PLACEMENT'))
                       )('VPIN')

        # routingPoints (used by regularWiring)
        MASK_id = pp.Keyword('MASK')('MASK')
        RECT_id = pp.Keyword('RECT')('RECT')
        VIRTUAL_id = pp.Keyword('VIRTUAL')('VIRTUAL')

        routingPoints_1 = (pp.Optional(MASK_id + number('maskNum'))
                           + pp.Group(pt)
                          )

        routingPoints_2 = (pp.Optional(MASK_id + number('viaMaskNum'))
                           + pp.NotAny(pp.Keyword('NEW') | pp.Keyword('RECT'))
                           + identifier('viaName')
                           + pp.Optional(ORIENT('orient'))
                          )

        routingPoints_3 = (pp.Optional(MASK_id + number('maskNum'))
                           + RECT_id
                           + pp.Group(pt)
                          )

        routingPoints_4 = (VIRTUAL_id + pp.Group(pt))

        routingPoints = (pp.Group(pt)
                         + pp.OneOrMore(routingPoints_1
                                        | routingPoints_2
                                        | routingPoints_3
                                        | routingPoints_4
                                       )
                        )

        # regularWiring
        regularWiring_ids = (pp.Keyword('COVER')
                             | pp.Keyword('FIXED')
                             | pp.Keyword('ROUTED')
                             | pp.Keyword('NOSHIELD')
                            )

        TAPER_RULE = ((pp.Keyword('TAPER') | pp.Keyword('TAPERRULE'))
                      + identifier('ruleName')
                     )

        STYLE = (pp.Keyword('STYLE') + identifier('layerName') + pp.OneOrMore(pt))

        regularWiring_Head = pp.Group(regularWiring_ids('WIRING_id')
                                      + identifier('layerName')
                                      + pp.Optional(TAPER_RULE)('TAPER_RULE')
                                      + pp.Optional(STYLE)('STYLE')
                                      + pp.OneOrMore(routingPoints)('routingPoints')
                                     )

        NEW_WIRING = pp.Group(pp.Keyword('NEW')('WIRING_id')
                              + identifier('layerName')
                              + pp.Optional(TAPER_RULE)('TAPER_RULE')
                              + pp.Optional(STYLE)('STYLE')
                              + pp.OneOrMore(routingPoints)('routingPoints')
                             )

        regularWiring = pp.Group(ws_net
                                 + pp.Group(regularWiring_Head)('WIRING_Head')
                                 + pp.Group(pp.ZeroOrMore(NEW_WIRING))('NEW_WIRING')
                                )('WIRING')

        # SUBNET
        SUBNET_regularWiring = pp.Group(pp.Group(regularWiring_Head)('WIRING_Head')
                                        + pp.Group(pp.ZeroOrMore(NEW_WIRING))('NEW_WIRING')
                                       )('WIRING')

        SUBNET_NONDEFAULTRULE = (pp.Keyword('NONDEFAULTRULE')
                                 + identifier('NONDEFAULTRULE_ruleName')
                                )

        SUBNET_pin_type = (pp.Keyword('VPIN')('VPIN')
                           | pp.Keyword('PIN')('PIN')
                           | identifier('compName')
                          )

        SUBNET = pp.Group(ws_net
                          + pp.Keyword('SUBNET')
                          + identifier('subnetName')
                          + pp.ZeroOrMore(LPAR
                                          + SUBNET_pin_type
                                          + identifier('pinName')
                                          + RPAR
                                         )
                          + pp.Optional(SUBNET_NONDEFAULTRULE)
                          + pp.ZeroOrMore(SUBNET_regularWiring)
                         )('SUBNET')

        # XTALK
        XTALK = (ws_net
                 + pp.Keyword('XTALK')
                 + number('XTALK_class')
                )

        # NONDEFAULTRULE
        NONDEFAULTRULE = (ws_net
                          + pp.Keyword('NONDEFAULTRULE')
                          + identifier('NONDEFAULTRULE_ruleName')
                         )

        # SOURCE
        SOURCE =(ws_net
                 + pp.Keyword('SOURCE')
                 + (pp.Keyword('DIST')
                    | pp.Keyword('NETLIST')
                    | pp.Keyword('TEST')
                    | pp.Keyword('TIMING')
                    | pp.Keyword('USER')
                   )('SOURCE')
                )

        # FIXEDBUMP
        FIXEDBUMP = (ws_net
                     + pp.Keyword('FIXEDBUMP')('FIXEDBUMP')
                    )

        # FREQUENCY
        FREQUENCY = (ws_net
                     + pp.Keyword('FREQUENCY')
                     + number('FREQUENCY')
                    )

        # ORIGINAL
        ORIGINAL = (ws_net
                    + pp.Keyword('ORIGINAL')
                    + identifier('ORIGINAL_netName')
                   )

        # USE > USE_ids
        USE_ids = (pp.Keyword('ANALOG')
                   | pp.Keyword('CLOCK')
                   | pp.Keyword('GROUND')
                   | pp.Keyword('POWER')
                   | pp.Keyword('RESET')
                   | pp.Keyword('SCAN')
                   | pp.Keyword('SIGNAL')
                   | pp.Keyword('TIEOFF')
                  )

        # USE
        USE = ws_net + pp.Keyword('USE') + USE_ids('USE')

        # PATTERN
        PATTERN_ids = (pp.Keyword('BALANCED')
                       | pp.Keyword('STEINER')
                       | pp.Keyword('TRUNK')
                       | pp.Keyword('WIREDLOGIC')
                      )

        PATTERN = (ws_net
                   + pp.Keyword('PATTERN')
                   + PATTERN_ids('PATTERN')
                  )

        # ESTCAP
        ESTCAP = (ws_net
                  + pp.Keyword('ESTCAP')
                  + number('ESTCAP_wireCap')
                 )

        # WEIGHT
        WEIGHT = (ws_net
                  + pp.Keyword('WEIGHT')
                  + number('WEIGHT')
                 )

        # PROPERTY
        PROPERTY = pp.Group(ws_net
                            + pp.Keyword('PROPERTY')
                            + pp.OneOrMore(identifier('propName')
                            + number('propVal'))
                           )('PROPERTY')

        # Refactor this!?
        if self.ignore_nets_route:
            regularWiring = pp.SkipTo((EOL + ws_net) | linebreak)

        net = pp.Group(pp.Suppress(begin_net)
                       + netName
                       + pp.Optional(SHIELDNET)
                       + pp.ZeroOrMore(VPIN)
                       + pp.ZeroOrMore(SUBNET)
                       + pp.Optional(XTALK)
                       + pp.Optional(NONDEFAULTRULE)
                       + pp.ZeroOrMore(regularWiring)
                       + pp.Optional(SOURCE)
                       + pp.Optional(FIXEDBUMP)
                       + pp.Optional(FREQUENCY)
                       + pp.Optional(ORIGINAL)
                       + pp.Optional(USE)
                       + pp.Optional(PATTERN)
                       + pp.Optional(ESTCAP)
                       + pp.Optional(WEIGHT)
                       + pp.ZeroOrMore(PROPERTY)
                       + linebreak
                      ).setResultsName('net', listAllMatches=True)

        nets = pp.Group(pp.Suppress(nets_id)
                        + number('numNets') + linebreak
                        + pp.ZeroOrMore(net)
                        + pp.Suppress(end_nets_id)
                       ).setResultsName('NETS')

        return nets

    # Parse the SPECIALNETS section of a .DEF file
    def parse_specialnets(self):
        EOL = pp.LineEnd().suppress()
        linebreak = pp.Suppress(";" + pp.LineEnd())
        identifier = pp.Word(pp.alphanums + '._“!<>/[]$#$%&‘*+,/:<=>?@[\]^_`{|}~')  # CONFLICT with '();'
        number = pp.pyparsing_common.number
        word = pp.Word(pp.alphas)
        LPAR = pp.Suppress('(')
        RPAR = pp.Suppress(')')
        ORIENT = (pp.Keyword('N')
                | pp.Keyword('S')
                | pp.Keyword('E')
                | pp.Keyword('W')
                | pp.Keyword('FN')
                | pp.Keyword('FS')
                | pp.Keyword('FE')
                | pp.Keyword('FW'))
        pt = LPAR + pp.OneOrMore(number | pp.Keyword('*')) + RPAR  # pair of x,y
        specialnets_id = pp.Suppress(pp.Keyword('SPECIALNETS'))
        end_specialnets_id = pp.Keyword("END SPECIALNETS").suppress()
        begin_specialnet = pp.Suppress(pp.Keyword('-'))
        ws_snet = pp.Suppress(pp.Keyword('+'))  # parameter division in NETS

        # netName
        netName_1 = pp.Group(LPAR
                             + identifier('compName') + identifier('pinName')
                             + pp.Optional(ws_snet + pp.Keyword('SYNTHESIZED'))('SYNTHESIZED')
                             + RPAR
                            )
        netName = identifier('netName') + pp.ZeroOrMore(netName_1).setResultsName('nets')

        # MASK
        MASK = pp.Group(pp.Keyword('MASK') + number('maskNum')).setResultsName('MASK')

        MASK_id = pp.Keyword('MASK')
        RECT_id = pp.Keyword('RECT')
        VIRTUAL_id = pp.Keyword('VIRTUAL')
        routingPoints_1 = pp.Optional(MASK('MASK') + number('maskNum')) + pp.Group(pt)
        routingPoints_2 = pp.Optional(MASK_id('MASK') + number('viaMaskNum')) + pp.NotAny(pp.Keyword('NEW') | pp.Keyword('RECT')) \
                                    + identifier('viaName') + pp.Optional(ORIENT('orient')) \
                        + pp.Optional(pp.Suppress(pp.Keyword('DO')) + number('numX') + pp.Suppress(pp.Keyword('BY')) + number('numY')
                                    + pp.Suppress(pp.Keyword('STEP')) + number('stepX') + number('stepY'))
        routingPoints = (pp.Group(pt) + pp.OneOrMore(routingPoints_1 | routingPoints_2))

        specialWiring_placement = (ws_snet + ((pp.Keyword('COVER')('PLACEMENT'))
                                              | (pp.Keyword('FIXED')('PLACEMENT'))
                                              | (pp.Keyword('ROUTED')('PLACEMENT'))
                                              | (pp.Keyword('SHIELD')('PLACEMENT') + identifier('shieldNetName'))
                                             )
                                   )

        specialWiring_1 = (pp.Optional(specialWiring_placement)
                           + pp.Optional(ws_snet + pp.Keyword('SHAPE') + identifier('shapeType'))
                           + pp.Optional(ws_snet + pp.Keyword('MASK') + number('maskNum'))
                           + ((ws_snet + pp.Keyword('POLYGON') + identifier('layerName') + pp.OneOrMore(pt))
                              | (ws_snet + pp.Keyword('RECT') + identifier('layerName') + pt + pt)
                              | (ws_snet + pp.Keyword('VIA') + identifier('viaName') + pp.Optional(ORIENT('orient')) + pp.OneOrMore(pt))
                             )
                          )

        SHAPE_elems = (pp.Keyword('RING') | pp.Keyword('PADRING') | pp.Keyword('BLOCKRING')
                       | pp.Keyword('STRIPE') | pp.Keyword('FOLLOWPIN') | pp.Keyword('IOWIRE')
                       | pp.Keyword('COREWIRE') | pp.Keyword('BLOCKWIRE') | pp.Keyword('BLOCKAGEWIRE')
                       | pp.Keyword('FILLWIRE') | pp.Keyword('FILLWIREOPC') | pp.Keyword('DRCFILL')
                      )

        specialWiring_2 = (specialWiring_placement
                           + identifier('layerName') + number('routeWidth')
                           + pp.Optional(ws_snet + pp.Keyword('SHAPE') + SHAPE_elems('SHAPE'))
                           + pp.Optional(ws_snet + pp.Keyword('STYLE') + number('styleNum'))
                           + routingPoints('routingPoints')
                           + pp.Group(pp.ZeroOrMore(pp.Group(pp.Keyword('NEW')
                                                             + identifier('layerName')
                                                             + number('routeWidth')
                                                             + pp.Optional(ws_snet
                                                                           + pp.Keyword('SHAPE')
                                                                           + SHAPE_elems('SHAPE')
                                                                          )
                                                             + pp.Optional(ws_snet
                                                                           + pp.Keyword('STYLE')
                                                                           + identifier('styleNum')
                                                                          )
                                                             + routingPoints('routingPoints')
                                                            )
                                                   )
                                     )
                          )('NEW')

        specialWiring = pp.Group(pp.OneOrMore(specialWiring_1 | specialWiring_2))('specialWiring')

        VOLTAGE = ws_snet + pp.Keyword('VOLTAGE') + number('VOLTAGE')

        SOURCE = ws_snet + pp.Keyword('SOURCE') + (pp.Keyword('DIST') | pp.Keyword('NETLIST') | pp.Keyword('TIMING') | pp.Keyword('USER'))

        FIXEDBUMP = ws_snet + pp.Keyword('FIXEDBUMP')('FIXEDBUMP')

        ORIGINAL = ws_snet + pp.Keyword('ORIGINAL') + identifier('ORIGINAL_netName')

        USE_ids = (pp.Keyword('ANALOG') | pp.Keyword('CLOCK') | pp.Keyword('GROUND') | pp.Keyword('POWER')
                 | pp.Keyword('RESET') | pp.Keyword('SCAN') | pp.Keyword('SIGNAL') | pp.Keyword('TIEOFF'))
        USE = ws_snet + pp.Keyword('USE') + USE_ids('USE')

        PATTERN_ids = (pp.Keyword('BALANCED') | pp.Keyword('STEINER') | pp.Keyword('TRUNK') | pp.Keyword('WIREDLOGIC'))
        PATTERN = ws_snet + pp.Keyword('PATTERN') + PATTERN_ids('PATTERN')

        ESTCAP = ws_snet + pp.Keyword('ESTCAP') + number('ESTCAP_wireCapacitance')

        WEIGHT = ws_snet + pp.Keyword('WEIGHT') + number('WEIGHT')

        PROPERTY = pp.Group(ws_snet
                            + pp.Keyword('PROPERTY')
                            + pp.OneOrMore(identifier('propName')
                            + number('propVal'))
                           )('PROPERTY')

        specialnet = pp.Group(begin_specialnet
                              + netName
                              + pp.Optional(VOLTAGE)
                              + pp.ZeroOrMore(specialWiring)
                              + pp.Optional(SOURCE)
                              + pp.Optional(FIXEDBUMP)
                              + pp.Optional(ORIGINAL)
                              + pp.Optional(USE)
                              + pp.Optional(PATTERN)
                              + pp.Optional(ESTCAP)
                              + pp.Optional(WEIGHT)
                              + pp.ZeroOrMore(PROPERTY)
                              + linebreak
                             ).setResultsName('specialnets', listAllMatches=True)

        specialnets = pp.Group(specialnets_id
                               + number('numNets') + linebreak
                               + pp.ZeroOrMore(specialnet)
                               + pp.Suppress(end_specialnets_id)
                              ).setResultsName('SPECIALNETS')

        return specialnets

    #
    def handle_design(self, token):
        print('DESIGN:')
        print(json.dumps(token['DESIGN'], indent=2))
        print()

    #
    def handle_dbuPerMicron(self, token):
        print('dbuPerMicron:')
        print(json.dumps(token['dbuPerMicron'], indent=2))
        print()

    #
    def handle_diearea(self, token):
        print('DIEAREA:')
        print(json.dumps(token['DIEAREA'], indent=2))
        print()

    #
    def handle_components(self, token):
        print('COMPONENTS:')
        # print(json.dumps(token['COMPONENTS'], indent=2))
        print()

    #
    def handle_pins(self, token):
        print('PINS:')
        # print(json.dumps(token['PINS'], indent=2))
        print()

    #
    def handle_specialnets(self, token):
        print('SPECIALNETS:')
        # print(json.dumps(token['SPECIALNETS'], indent=2))
        print()

    #
    def handle_nets(self, token):
        print('NETS:')
        # print(json.dumps(token['NETS'], indent=2))
        print()


def main():
    _def = DefParser()
    _def.run()


if __name__ == "__main__":
    main()
