import renpy
from renpy import ast, config, game, python, exports

from modloader.modclass import Mod, loadable_mod

import jz_magmalink as ml


def _show_charmenu(calling_node):
    ast.next_node(calling_node.next)
    ast.statement_name("bannermod_four_menu")
    
    menu = ml.node(calling_node).search_menu()
    choices = []

    for i, (label, condition, block) in enumerate(menu.node.items):
        if config.say_menu_text_filter:
            label = config.say_menu_text_filter(label)
        
        if block is None:
            renpy.error("Angels with Scaly Wings character menus should not have menu labels without blocks.")
        else:
            if python.py_eval(condition):
                choices.append(((label % exports.tag_quoting_dict) if config.old_substitutions else label, i))

    ast.say_menu_with(menu.node.with_, game.interface.set_transition)

    if not choices:
        return None

    choice = exports.display_menu(choices, screen='bannermenu_four_choice')

    if choice is not None:
        ast.next_node(menu.node.items[choice][2][0])

    return True

def link_bannermod():
    c1csplayed = ml.find_label("chapter1chars") \
        .search_if("chapter1csplayed == 0")

    c2csplayed = ml.find_label("chapter2chars") \
        .search_if("playmessage == True") \
        .search_if("chapter2csplayed == 0")

    cpaginationifs = [
        ("bannermod_c1pm1",c1csplayed.branch().search_say("(What should I do?)")),
        ("bannermod_c1pm2",c1csplayed.branch('chapter1csplayed == 1').search_say("(More free time. What should I do?)")),
        ("bannermod_c2pm1",c2csplayed.branch().search_if('chapter2count >= 7')),
        ("bannermod_c2pm2",c2csplayed.branch('chapter2csplayed == 1').search_if('chapter2count >= 7')),
        ("bannermod_c3pm1",ml.find_label('chapter3chars2').search_if('chapter3count >= 7')),
        ("bannermod_c3pm2",ml.find_label('chapter3chars3').search_if('chapter3count >= 7')),
        ("bannermod_c4pm1",ml.find_label('chapter4chars2').search_if('chapter4count >= 7')),
        ("bannermod_c4pm2",ml.find_label('chapter4chars3').search_if('chapter4count >= 7')),
    ]

    for tag, paginationif in cpaginationifs:
        # Disabling of Saunders' pagination is left to MagmaLink
        ml.ast_utils._create_hook(node_from=paginationif.node, func=_show_charmenu, tag=tag)

    c5menutrailer = ml.find_label('chapter5') \
        .search_say("(Today is the day of the big fireworks. Who shall I bring?)") \
        ._search(lambda n: isinstance(n.next, ast.Menu), 50, "Chapter 5 character menu not within 50 nodes of 'if loremdead == False'")

    ml.ast_utils._create_hook(node_from=c5menutrailer.node, func=_show_charmenu, tag="c5pm") 

@loadable_mod
class BannerMod(Mod):
    name = "BannerMenu"
    version = "v0.5"
    author = "4onen"
    nsfw = False
    dependencies = ["MagmaLink", "?Chaos_Knight core mod."]

    @classmethod
    def mod_load(cls):
        # Testing link
        # ( ml.find_label('seccont')
        #     .hook_to('bannermod_test_scene')
        # )

        link_bannermod()

    @staticmethod
    def mod_complete():
        pass
