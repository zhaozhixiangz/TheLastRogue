import action
import constants
import colors
from counter import Counter
import dungeoncreatorvisualizer
from equipment import EquipmentSlots
import gametime
import geometry as geo
import graphic
import gui
import menu
import rectfactory
import sacrifice
import save
import settings
import state
import style
import icon


def _main_menu(ui_state, state_stack, player_name_func, game_state_factory, test_game_state_factory):
    """
    Creates the first menu of the game.
    """
    continue_game_function = lambda: ui_state.current_stack.push(save.load_first_game())
    start_game_function = lambda: ui_state.current_stack.push(game_state_factory(player_name_func()))
    start_test_game_function = lambda: ui_state.current_stack.push(test_game_state_factory(player_name_func()))
    quit_game_function = lambda: ui_state.current_stack.pop()
    dungeon_visualizer_function = \
        lambda: ui_state.current_stack.push(dungeoncreatorvisualizer.DungeonCreatorVisualizer())

    no_icon = graphic.GraphicChar(None, colors.BLACK, " ")
    gun_icon = graphic.GraphicChar(None, colors.WHITE, icon.GUN)
    menu_items = []

    continue_game_option = menu.MenuOptionWithSymbols("Continue", gun_icon, no_icon, [continue_game_function],
                                                      save.is_there_a_saved_game)
    menu_items.append(continue_game_option)

    start_game_option = \
        menu.MenuOptionWithSymbols("New Game", gun_icon, no_icon, [start_game_function])
    menu_items.append(start_game_option)

    if settings.DEV_MODE_FLAG:
        start_test_game_option = \
            menu.MenuOptionWithSymbols("Test Dungeon", gun_icon, no_icon, [start_test_game_function])
        menu_items.append(start_test_game_option)

        dungeon_creator_option = \
            menu.MenuOptionWithSymbols("Dungeon Generator", gun_icon, no_icon, [dungeon_visualizer_function])
        menu_items.append(dungeon_creator_option)

    quit_option = menu.MenuOptionWithSymbols("Quit", gun_icon, no_icon, [quit_game_function])
    menu_items.append(quit_option)

    temp_position = (0, 0)
    return menu.StaticMenu(temp_position, menu_items, state_stack, margin=style.menu_theme.margin,
                           vertical_space=1, vi_keys_accepted=False)


def get_save_quit_menu(player, state_stack):
    options = []
    game_state = player.game_state.value
    exit_menu_function = menu.BackToGameFunction(state_stack)
    save_and_quit_graphic_active = graphic.GraphicChar(None, colors.WHITE, icon.GUNSLINGER_THIN)
    save_and_quit_graphic_inactive = graphic.GraphicChar(None, colors.GRAY, icon.GUNSLINGER_THIN)
    options.append(menu.MenuOptionWithSymbols("Save and Quit", save_and_quit_graphic_active,
                                              save_and_quit_graphic_inactive,
                                              [lambda: save.save(game_state), exit_menu_function,
                                               game_state.current_stack.pop,
                                               (lambda: player.actor.add_energy_spent(gametime.single_turn))]))

    give_up_graphic_active = graphic.GraphicChar(None, colors.WHITE, icon.SKULL)
    give_up_graphic_inactive = graphic.GraphicChar(None, colors.GRAY, icon.SKULL)
    options.append(menu.MenuOptionWithSymbols("Give Up", give_up_graphic_active, give_up_graphic_inactive,
                                              [player.health_modifier.kill, exit_menu_function,
                                               (lambda: player.actor.add_energy_spent(gametime.single_turn))]))

    return get_menu_with_options(options, state_stack, 6, 5)


def get_menu_with_options(options, state_stack, x_border=4, y_border=5):
    temp_position = (-1, -1)
    main_menu = menu.StaticMenu(temp_position, options, state_stack, margin=style.menu_theme.margin, vertical_space=1)
    main_menu_rect = rectfactory.ratio_of_screen_rect(main_menu.width + x_border, main_menu.height + y_border - 1, 0.5,
                                                      0.8)
    main_menu.offset = main_menu_rect.top_left

    background_rect = get_menu_background(main_menu_rect)
    ui_state = state.UIState(gui.UIElementList([background_rect, main_menu]))
    return ui_state


def get_item_menu_stack_panel_template(heading_text, heading_icon=None):
    menu_stack_panel = gui.StackPanelVertical((2, 2), vertical_space=1)
    heading_stack = gui.StackPanelHorizontal((0, 1), horizontal_space=1)
    if heading_icon:
        heading_stack.append(gui.SymbolUIElement((0, 0), heading_icon))
    heading_stack.append(gui.TextBox(heading_text, (0, 0), colors.INVENTORY_HEADING))
    menu_stack_panel.append(heading_stack)
    return menu_stack_panel


def _get_item_action_menu_option(item, player, state_stack):
    menu_item_action = menu.OpenItemActionMenuAction(state_stack, item, player)
    menu_item_can_activate_function = (lambda: (len(item.get_children_with_tag("user_action")) >= 1))
    item_icon = item.graphic_char
    menu_option = menu.MenuOptionWithSymbols(_get_item_option_text(item), item_icon, item_icon, [menu_item_action],
                                             menu_item_can_activate_function, payload=item)
    return menu_option


def _get_item_menu_composition(item_description_card, menu_stack_panel):
    inventory_menu_bg = gui.StyledRectangle(rectfactory.right_side_menu_rect(), style.MinimalChestStyle())
    inventory_gui = gui.UIElementList([inventory_menu_bg, menu_stack_panel])
    inventory_stack_panel = gui.StackPanelHorizontal((0, 0), alignment=gui.StackPanelHorizontal.ALIGN_BOTTOM)
    inventory_stack_panel.append(item_description_card)
    inventory_stack_panel.append(inventory_gui)
    dock = gui.UIDock(rectfactory.full_screen_rect())
    dock.bottom_right = inventory_stack_panel
    return state.UIState(dock)


def inventory_menu(player, state_stack):
    menu_stack_panel = get_item_menu_stack_panel_template("Inventory",
                                                          graphic.GraphicChar(None, colors.INVENTORY_HEADING,
                                                                              icon.INVENTORY_ICON))
    item_description_card = gui.new_item_description_card()
    menu_items = []
    for item in player.inventory.get_items_sorted():
        menu_option = _get_item_action_menu_option(item, player, state_stack)
        menu_items.append(menu_option)

    inventory_menu = menu.StaticMenu((0, 1), menu_items, state_stack, (0, 0), vertical_space=0,
                                     selected_payload_callback=(lambda item: item_description_card.set_item(item)))
    menu_stack_panel.append(inventory_menu)

    return _get_item_menu_composition(item_description_card, menu_stack_panel)


def _get_item_option_text(item):
    if item.has("stacker") and item.stacker.size > 1:
        return item.description.name + " (" + str(item.stacker.size) + ")"
    if item.has("charge"):
        return item.description.name + " [" + str(item.charge.charges) + "]"
    return item.description.name


def _has_item_with_action_tag(player, item_action_tag):
    for item in player.inventory.get_items_sorted():
        if len(item.get_children_with_tag(item_action_tag)) > 0:
            return True
    return False


def _get_item_action_option(item, item_action, player, stack_pop_function):
    item_graphic = item.graphic_char
    item_action_list = [action.DelayedFunctionCall(item_action.act, source_entity=player,
                                                   target_entity=player), stack_pop_function]
    can_activate = (lambda: item_action.can_act(source_entity=player,
                                                target_entity=player))
    item_action_option = menu.MenuOptionWithSymbols(
        _get_item_option_text(item), item_graphic, item_graphic,
        item_action_list, can_activate=can_activate, payload=item)
    return item_action_option


def filtered_by_action_item_menu(player, state_stack, item_action_tag, heading_text):
    menu_stack_panel = get_item_menu_stack_panel_template(heading_text,
                                                          graphic.GraphicChar(None,
                                                                              colors.INVENTORY_HEADING,
                                                                              icon.INVENTORY_ICON))
    item_description_card = gui.new_item_description_card()
    stack_pop_function = menu.BackToGameFunction(state_stack)
    menu_items = []
    for item in player.inventory.get_items_sorted():
        if len(item.get_children_with_tag(item_action_tag)) > 0:
            item_action = item.get_children_with_tag(item_action_tag)[0]
            item_action_option = _get_item_action_option(item, item_action, player, stack_pop_function)
            menu_items.append(item_action_option)

    action_menu = menu.StaticMenu((0, 1), menu_items, state_stack,
                                  (0, 0), vertical_space=0, selected_payload_callback=(lambda item: item_description_card.set_item(item)))
    menu_stack_panel.append(action_menu)
    return _get_item_menu_composition(item_description_card, menu_stack_panel)


def _get_item_callback_option(item, callback, can_callback_activate, player, stack_pop_function):
    item_graphic = item.graphic_char
    item_action_list = [(lambda item=item: callback(item, source_entity=player,
                                                    target_entity=player)), stack_pop_function]
    can_activate = (lambda: can_callback_activate())
    item_action_option = menu.MenuOptionWithSymbols(
        _get_item_option_text(item), item_graphic, item_graphic,
        item_action_list, can_activate=can_activate, payload=item)
    return item_action_option


def item_type_menu_callback_menu(player, state_stack, item_type, heading_text, item_callback,
                                 can_callback_activate=(lambda: True)):
    menu_stack_panel = get_item_menu_stack_panel_template(heading_text,
                                                          graphic.GraphicChar(None,
                                                                              colors.INVENTORY_HEADING,
                                                                              icon.INVENTORY_ICON))
    item_description_card = gui.new_item_description_card()
    stack_pop_function = menu.BackToGameFunction(state_stack)
    menu_items = []
    for item in player.inventory.get_items_sorted():
        if item.item_type.value == item_type:
            item_action_option = _get_item_callback_option(item, item_callback, can_callback_activate,
                                                           player, stack_pop_function)
            menu_items.append(item_action_option)

    _equip_menu = menu.StaticMenu((0, 1), menu_items, state_stack, (0, 0), vertical_space=0,
                                  selected_payload_callback=(lambda item: item_description_card.set_item(item)))
    menu_stack_panel.append(_equip_menu)
    return _get_item_menu_composition(item_description_card, menu_stack_panel)


def item_actions_menu(item, player, state_stack):
    menu_stack_panel = gui.StackPanelVertical((2, 2), vertical_space=1)
    heading_stack = gui.StackPanelHorizontal((0, 1), horizontal_space=1)
    heading_stack.append(gui.SymbolUIElement((0, 0), item.graphic_char))
    heading = gui.TextBox(item.description.name, (0, 0), colors.INVENTORY_HEADING)
    heading_stack.append(heading)
    menu_stack_panel.append(heading_stack)

    item_actions_menu = menu.ItemActionsMenu((0, 0), item, player, state_stack, margin=(2, 2))
    menu_stack_panel.append(item_actions_menu)
    inventory_menu_bg = gui.StyledRectangle(rectfactory.right_side_menu_rect(),
                                            style.rogue_classic_theme.rect_style)

    dock = gui.UIDock(rectfactory.full_screen_rect())
    ui_elements = [inventory_menu_bg, menu_stack_panel]
    dock.bottom_right = gui.UIElementList(ui_elements)
    ui_state = state.UIState(dock)
    return ui_state


def equipment_menu(player, state_stack):
    menu_stack_panel = gui.StackPanelVertical((0, 0), margin=(0, 0))
    heading = gui.TextBox("Equipment", (2, 1), colors.INVENTORY_HEADING, (2, 2))
    menu_stack_panel.append(heading)

    equipment_menu_bg = gui.StyledRectangle(rectfactory.right_side_menu_rect(),
                                            style.rogue_classic_theme.rect_style)

    item_description_card = gui.new_item_description_card()
    resulting_menu = menu.EquipmentMenu((0, 0), player, state_stack, selected_payload_callback=(lambda item: item_description_card.set_item(item)), margin=(2, 1))
    menu_stack_panel.append(resulting_menu)

    equipment_gui = gui.UIElementList([equipment_menu_bg, menu_stack_panel])

    equipment_stack_panel = gui.StackPanelHorizontal((0, 0), alignment=gui.StackPanelHorizontal.ALIGN_BOTTOM)
    equipment_stack_panel.append(item_description_card)
    equipment_stack_panel.append(equipment_gui)

    dock = gui.UIDock(rectfactory.full_screen_rect())
    dock.bottom_right = equipment_stack_panel
    return state.UIState(dock)


def equipment_slot_menu(player, equipment_slot, state_stack):
    """
    Creates a menu which shows the possible actions
    that can be taken on a given equipment_slot.
    """
    menu_stack_panel = gui.StackPanelVertical((0, 0), margin=(0, 0))
    heading = gui.TextBox("Change " + equipment_slot.name, (2, 1), colors.INVENTORY_HEADING, (2, 2))
    menu_stack_panel.append(heading)

    item_description_card = gui.new_item_description_card()
    resulting_menu = menu.EquipSlotMenu((0, 0), player, equipment_slot, state_stack, (lambda item: item_description_card.set_item(item)), (2, 1))
    menu_stack_panel.append(resulting_menu)

    equipment_menu_bg = gui.StyledRectangle(rectfactory.right_side_menu_rect(),
                                            style.rogue_classic_theme.rect_style)
    equipment_slot_gui = gui.UIElementList([equipment_menu_bg, menu_stack_panel])

    equipment_slot_stack_panel = gui.StackPanelHorizontal((0, 0), alignment=gui.StackPanelHorizontal.ALIGN_BOTTOM)
    equipment_slot_stack_panel.append(item_description_card)
    equipment_slot_stack_panel.append(equipment_slot_gui)

    dock = gui.UIDock(rectfactory.full_screen_rect())
    dock.bottom_right = equipment_slot_stack_panel
    return state.UIState(dock)


def get_menu_background(rectangle, rect_style=style.menu_theme.rect_style, h_split=[], v_split=[]):
    return gui.StyledRectangle(rectangle, rect_style, h_split=h_split, v_split=v_split)


def context_menu(player, state_stack):
    current_dungeon_feature = (player.dungeon_level.value.get_tile(player.position.value).get_dungeon_feature())
    context_options = []
    stack_pop_function = menu.BackToGameFunction(state_stack)
    if not current_dungeon_feature is None:
        context_options.extend(get_dungeon_feature_menu_options(player, stack_pop_function))

    status_menu = player_status_menu(player)
    open_status_option = menu.MenuOption("Player Status", [lambda: state_stack.push(status_menu)])
    context_options.append(open_status_option)

    inventory_menu_opt = inventory_menu(player, state_stack)
    open_inventory_option = menu.MenuOption("Inventory", [lambda: state_stack.push(inventory_menu_opt)],
                                            (lambda: not player.inventory.is_empty()))
    context_options.append(open_inventory_option)

    equipment_menu_opt = equipment_menu(player, state_stack)
    open_equipment_option = menu.MenuOption("Equipment", [lambda: state_stack.push(equipment_menu_opt)])
    context_options.append(open_equipment_option)

    context_menu_rect = rectfactory.center_of_screen_rect(max(option.width for option in context_options) + 4,
                                                          len(context_options) * 2 + 3)
    resulting_menu = menu.StaticMenu(context_menu_rect.top_left, context_options, state_stack,
                                     margin=style.menu_theme.margin)
    background_rect = get_menu_background(context_menu_rect)

    ui_elements = [background_rect, resulting_menu]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def new_player_status_stack(player, width):
    text_margin = width - 3
    text_box_margin = (0, 0)
    strength_text_box = gui.TextBox("Str" + str(player.strength.value).rjust(text_margin), text_box_margin,
                                    colors.ORANGE)
    armor_text_box = gui.TextBox("Def" + str(player.armor.value).rjust(text_margin), text_box_margin, colors.GRAY)
    evasion_text_box = gui.TextBox("Eva" + str(player.evasion.value).rjust(text_margin), text_box_margin, colors.GREEN)
    stealth_text_box = gui.TextBox("Sth" + str(player.stealth.value).rjust(text_margin), text_box_margin, colors.BLUE)
    movement_speed_text_box = gui.TextBox("Mov" + str(int(120.0 / player.movement_speed.value * 10)).rjust(text_margin),
                                          text_box_margin, colors.CHAMPAGNE)

    status_stack_panel = gui.StackPanelVertical((0, 0), alignment=gui.StackPanelVertical.ALIGN_LEFT, vertical_space=0)
    status_stack_panel.append(strength_text_box)
    status_stack_panel.append(armor_text_box)
    status_stack_panel.append(evasion_text_box)
    status_stack_panel.append(stealth_text_box)
    status_stack_panel.append(movement_speed_text_box)
    return status_stack_panel


def new_player_weapon_table(player, width):
    equipment = player.equipment
    if equipment.slot_is_equiped(EquipmentSlots.MELEE_WEAPON):
        melee_graphic = equipment.get(EquipmentSlots.MELEE_WEAPON).graphic_char
    else:
        melee_graphic = graphic.GraphicChar(None, colors.WHITE, icon.BIG_CENTER_DOT)
    melee_damage = str(player.melee_attacker.min_damage) + "-" + str(player.melee_attacker.max_damage)
    melee_accuracy = player.melee_attacker.accuracy
    melee_crit_chance = "{:.0f}".format(player.melee_attacker.crit_chance * 100) + "%"

    if equipment.slot_is_equiped(EquipmentSlots.RANGED_WEAPON):
        range_graphic = equipment.get(EquipmentSlots.RANGED_WEAPON).graphic_char
    else:
        range_graphic = graphic.GraphicChar(None, colors.GRAY, icon.STONE)
    range_damage = str(player.ranged_attacker.min_damage) + "-" + str(player.ranged_attacker.max_damage)
    range_accuracy = player.ranged_attacker.accuracy
    range_crit_chance = "{:.0f}".format(player.ranged_attacker.crit_chance * 100) + "%"

    value_width = 3
    text_box_margin = (0, 0)
    heading_stack_panel = gui.StackPanelHorizontal((0, 0), alignment=gui.StackPanelHorizontal.ALIGN_TOP,
                                                   horizontal_space=0)
    heading_stack_panel.append(gui.HorizontalSpace(6))
    heading_stack_panel.append(gui.SymbolUIElement((0, 0), melee_graphic))
    heading_stack_panel.append(gui.HorizontalSpace(3))
    heading_stack_panel.append(gui.SymbolUIElement((0, 0), range_graphic))
    damage_text_box = gui.TextBox("Dmg " + str(melee_damage).rjust(value_width) +
                                  " " + str(range_damage).rjust(value_width),
                                  text_box_margin, colors.WHITE)
    hit_text_box = gui.TextBox("Hit " + str(melee_accuracy).rjust(value_width) +
                               " " + str(range_accuracy).rjust(value_width),
                               text_box_margin, colors.YELLOW)
    crit_chance_text_box = gui.TextBox("Cri " + str(melee_crit_chance).rjust(value_width) +
                                       " " + str(range_crit_chance).rjust(value_width),
                                       text_box_margin, colors.RED)

    status_stack_panel = gui.StackPanelVertical((0, 0), alignment=gui.StackPanelVertical.ALIGN_LEFT,
                                                vertical_space=0)
    status_stack_panel.append(heading_stack_panel)
    status_stack_panel.append(gui.VerticalSpace(1))
    status_stack_panel.append(damage_text_box)
    status_stack_panel.append(hit_text_box)
    status_stack_panel.append(crit_chance_text_box)
    return status_stack_panel


def player_status_menu(player):
    split_width = 27
    content_padding = (2, 2)
    player_status_stack_panel = gui.StackPanelVertical(geo.add_2d((0, 0), content_padding),
                                                       alignment=gui.StackPanelVertical.ALIGN_LEFT,
                                                       vertical_space=1)
    player_status_stack_panel_row_1 = gui.StackPanelHorizontal((0, 0), alignment=gui.StackPanelHorizontal.ALIGN_TOP,
                                                               horizontal_space=1)
    player_status_stack_panel.append(player_status_stack_panel_row_1)
    player_status_stack_panel_row_1.append(gui.BigSymbolUIElement((0, 0), player.graphic_char))
    player_description_stack = gui.StackPanelVertical((0, 0), alignment=gui.StackPanelVertical.ALIGN_LEFT,
                                                      vertical_space=1)
    player_status_stack_panel_row_1.append(player_description_stack)
    player_description_stack.append(gui.TextBox(player.description.name, (2, 0), colors.WHITE))
    player_description_stack.append(gui.TextBox(player.race.value + "\n" + player.job.value, (2, 0), colors.WHITE))

    player_description_stack.append(gui.new_player_hp_bar(12, player.health.hp))
    player_description_stack.append(gui.new_player_sanity_bar(12, Counter(10, 10)))

    player_status_stack_panel_row_2 = gui.StackPanelHorizontal((0, 0), alignment=gui.StackPanelHorizontal.ALIGN_TOP,
                                                               horizontal_space=3)
    player_status_stack_panel.append(player_status_stack_panel_row_2)
    player_status_stack_panel_row_2.append(new_player_status_stack(player, 8))
    player_status_stack_panel_row_2.append(new_player_weapon_table(player, 8))

    description_card = gui.new_item_description_card()
    power_list = get_power_list(player, description_card)
    if len(power_list.menu_items) > 0:
        player_status_stack_panel.append(gui.VerticalSpace(1))
    player_status_stack_panel.append(power_list)

    bg_rect_height = (player_status_stack_panel.total_height + 4)
    bg_rect = rectfactory.center_of_screen_rect(split_width, bg_rect_height)

    player_status_stack_panel.offset = geo.add_2d(bg_rect.top_left, (2, 2))

    styled_bg_rect = get_menu_background(bg_rect, style.rogue_classic_theme.rect_style)

    dock = gui.UIDock(rectfactory.full_screen_rect())
    dock.bottom = description_card
    return state.UIState(gui.UIElementList([styled_bg_rect, player_status_stack_panel, dock]))


#TODO: This is not used now, but it should, it's pretty good! Need multiple menus at once for that.
def get_status_list(player):
    context_options = []
    state_stack = player.game_state.value.menu_prompt_stack
    for status in player.status_bar.statuses:
        print status, status.graphic_char, status.graphic_char.color_fg
        status_option = menu.MenuOptionWithSymbols(status.name, status.graphic_char, status.graphic_char,
            [], (lambda: True))
        context_options.append(status_option)
    resulting_menu = menu.StaticMenu((0, 0), context_options, state_stack,
                                     margin=style.menu_theme.margin)
    return gui.UIElementList([resulting_menu])


def get_power_list(player, description_card):
    options = []
    state_stack = player.game_state.value.menu_prompt_stack
    for power in player.get_children_with_tag("power"):
        status_option = menu.MenuOption(power.description.name, [], (lambda: True), payload=power)
        options.append(status_option)
    resulting_menu = menu.StaticMenu((0, 0), options, state_stack,
                                     selected_payload_callback=(lambda item, dc=description_card: dc.set_item(item)))
    return resulting_menu


def sacrifice_menu(player, powers, post_power_gain_function):
    game_state = player.game_state.value
    state_stack = game_state.menu_prompt_stack
    context_options = []
    stack_pop_function = menu.BackToGameFunction(state_stack)
    width = 24

    for power in powers:
        power_caption = power.description.name + str(power.buy_cost).rjust(width - len(power.description.name))
        power_option = menu.MenuOption(power_caption, [lambda p=power: player.set_child(p),
                                                       lambda p=power: p.on_power_gained(),
                                                       lambda p=power: sacrifice.sacrifice_health(player, p.buy_cost),
                                                       lambda: player.actor.add_energy_spent(gametime.single_turn),
                                                       post_power_gain_function,
                                                       stack_pop_function],
                                       (lambda: player.health.hp.value > power.buy_cost), payload=power)
        context_options.append(power_option)

    cancel_option = menu.MenuOption("Cancel", [stack_pop_function], (lambda: True))
    context_options.append(cancel_option)

    tmp = (0, 0)
    menu_stack_panel = gui.StackPanelVertical(tmp, style.menu_theme.margin, vertical_space=0,
                                              alignment=gui.StackPanelVertical.ALIGN_CENTER)

    heading_stack_panel = gui.StackPanelHorizontal((0, 0), (0, 0), horizontal_space=2)
    menu_stack_panel.append(heading_stack_panel)
    if any(powers):
        power_caption = "Power" + str("Cost").rjust(width - len("Cost   "))
        heading_stack_panel.append(gui.TextBox(power_caption, (1, 0), colors.GRAY))
        heading_stack_panel.append(gui.SymbolUIElement((0, 0), graphic.GraphicChar(colors.DARK_BLUE, colors.HP_BAR_FULL, icon.HEALTH_STAT)))
        menu_stack_panel.append(gui.VerticalSpace(2))
    else:
        power_caption = "There are no more powers."
        menu_stack_panel.append(gui.VerticalSpace(4))
        heading_stack_panel.append(gui.TextBox(power_caption, (1, 0), colors.GRAY))

    item_description_card = gui.new_item_description_card()
    resulting_menu = menu.StaticMenu((0, 0), context_options, state_stack, selected_payload_callback=(lambda item: item_description_card.set_item(item)))
    menu_stack_panel.append(resulting_menu)

    context_menu_rect = rectfactory.center_of_screen_rect(max(menu_stack_panel.total_width, 24),
                                                          max(menu_stack_panel.total_height, 6))
    menu_stack_panel.offset = context_menu_rect.top_left
    background_rect = get_menu_background(context_menu_rect, style.sacrifice_menu_theme.rect_style)

    dock = gui.UIDock(rectfactory.full_screen_rect())
    dock.bottom = item_description_card

    ui_elements = [background_rect, menu_stack_panel, dock]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def get_tile_actions(player):
    tile = player.dungeon_level.value.get_tile(player.position.value)
    dungeon_feature = tile.get_dungeon_feature()
    actions = []
    if not dungeon_feature is None:
        actions = dungeon_feature.get_children_with_tag("user_action")
    return actions


def get_dungeon_feature_menu_options(player, stack_pop_function):
    feature_options = []
    game_state = player.game_state.value
    for feature_action in get_tile_actions(player):
        feature_option = feature_action.delayed_act(source_entity=player,
                                                     target_entity=player,
                                                     game_state=game_state)
        functions = [feature_option, stack_pop_function]
        feature_options.append(menu.MenuOption(feature_action.name, functions, feature_action.can_act))
    return feature_options


def title_screen(state_stack, game_state_factory, test_game_state_factory):

    bg_color = colors.DARKNESS
    logo_fg = colors.RED

    _ = graphic.GraphicChar(bg_color, bg_color, " ")
    x = graphic.GraphicChar(logo_fg, logo_fg, " ")
    d = graphic.GraphicChar(bg_color, logo_fg, icon.DIAGONAL_SE)
    b = graphic.GraphicChar(bg_color, logo_fg, icon.DIAGONAL_SW)
    p = graphic.GraphicChar(logo_fg, bg_color, icon.DIAGONAL_SE)
    q = graphic.GraphicChar(logo_fg, bg_color, icon.DIAGONAL_SW)


    graphic_matrix = [
    [_,_,_,x,x,x,_,_,x,_,x,_,_,x,x,x,_,_,_,_,_,_,_,x,_,_,_,_,d,x,b,_,_,d,x,p,_,_,x,x,x,_,_],
    [_,_,_,_,x,_,_,_,x,_,x,_,_,x,_,_,_,_,_,_,_,_,_,x,_,_,_,_,x,_,x,_,_,x,_,_,_,_,_,x,_,_,_],
    [_,_,_,_,x,_,_,_,x,x,x,_,_,x,x,_,_,_,_,_,_,_,_,x,_,_,_,_,x,x,x,_,_,q,x,b,_,_,_,x,_,_,_],
    [_,_,_,_,x,_,_,_,x,_,x,_,_,x,_,_,_,_,_,_,_,_,_,x,_,_,_,_,x,_,x,_,_,_,_,x,_,_,_,x,_,_,_],
    [_,_,_,_,x,_,_,_,x,_,x,_,_,x,x,x,_,_,_,_,_,_,_,x,x,x,_,_,x,_,x,_,_,x,x,p,_,_,_,x,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [q,x,x,x,x,x,x,b,_,_,d,x,x,x,x,x,b,_,_,d,x,x,x,x,x,b,_,q,x,x,p,_,q,x,x,p,q,x,x,x,x,x,x],
    [_,x,x,_,_,q,x,x,_,_,x,x,p,_,q,x,x,_,_,x,x,p,_,q,x,x,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,q],
    [_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,_,_,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,_],
    [_,x,x,_,_,d,x,x,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,_,_,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,_],
    [_,x,x,x,x,x,x,p,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,x,x,x,p,_,x,x,_,_,_,x,x,_,_,x,x,x,x,p,_],
    [_,x,x,q,x,b,_,_,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,_],
    [_,x,x,_,q,x,b,_,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,x,x,_,_,x,x,_,_,_,_],
    [_,x,x,_,_,q,x,b,_,_,x,x,b,_,d,x,x,_,_,x,x,b,_,d,x,x,_,_,x,x,b,_,d,x,x,_,_,x,x,_,_,_,d],
    [d,x,x,b,_,_,x,x,b,_,q,x,x,x,x,x,p,_,_,q,x,x,x,x,x,p,_,_,q,x,x,x,x,x,p,_,d,x,x,x,x,x,x]
    ]

    logo = gui.GraphicCharMatrix(graphic_matrix)
    line = gui.HorizontalLine(graphic.GraphicChar(bg_color, colors.RED, icon.H_LINE), settings.SCREEN_WIDTH + 1)
    title_stack_panel = gui.StackPanelVertical((0, 0), alignment=gui.StackPanelVertical.ALIGN_CENTER)
    title_stack_panel.append(gui.VerticalSpace(int(settings.SCREEN_HEIGHT * 0.2)))
    title_stack_panel.append(line)
    title_stack_panel.append(gui.VerticalSpace(1))
    title_stack_panel.append(logo)
    title_stack_panel.append(gui.VerticalSpace(1))
    title_stack_panel.append(line)
    title_stack_panel.append(gui.VerticalSpace(5))

    bg_rect = gui.FilledRectangle(rectfactory.full_screen_rect(), bg_color)

    ui_state = state.UIState(gui.UIElementList(None))
    hero_name_type_writer = gui.TypeWriter((0, 0), colors.WHITE, colors.GRAY_D, constants.LEFT_SIDE_BAR_WIDTH - 4,
                                           default_text=settings.DEFAULT_PLAYER_NAME)
    main_menu = _main_menu(ui_state, state_stack, lambda: hero_name_type_writer.text, game_state_factory, test_game_state_factory)

    name_heading = gui.TextBox("Name:", (0, 0), colors.CYAN_D, (0, 1))
    menu_stack_panel = gui.StackPanelVertical((0, 0), (0, 0), vertical_space=0,
                                              alignment=gui.StackPanelVertical.ALIGN_CENTER)
    menu_stack_panel.append(name_heading)
    menu_stack_panel.append(hero_name_type_writer)
    menu_stack_panel.append(main_menu)

    dock = gui.UIDock(rectfactory.full_screen_rect())
    dock.bottom = menu_stack_panel

    type_writer_highlight_update = \
        gui.UpdateCallOnlyElement(
            [lambda: type_writer_highlight_update_function(name_heading, hero_name_type_writer,
                                                           main_menu, colors.WHITE,
                                                           colors.GRAY_D, [1, 2])])

    ui_state.ui_element.elements = [bg_rect, title_stack_panel, dock, type_writer_highlight_update]
    return ui_state


def type_writer_highlight_update_function(label, type_writer, menu, active_fg_color, inactive_fg_color,
                                          active_indices):
    """
Function for manipulating typewriter color, depending on selected menu item.

This is a ugly hack, remove if some event system is implemented for menus.
"""
    if menu.selected_index in active_indices:
        label.color_fg = active_fg_color
        type_writer.is_active = True
    else:
        label.color_fg = inactive_fg_color
        type_writer.is_active = False


def victory_screen(state_stack):
    victory_stack_panel = gui.StackPanelVertical((0, 0), alignment=gui.StackPanelVertical.ALIGN_CENTER)
    line = gui.HorizontalLine(graphic.GraphicChar(None, colors.YELLOW, icon.H_LINE), settings.SCREEN_WIDTH + 1)
    victory_text = gui.TextBox("A WINNER IS YOU", (0, 0), colors.WHITE)
    ironic_text = \
        gui.TextBox("Good job! No seriously, I bet it was real hard...",
                    (0, 0), colors.YELLOW_D)

    continue_option = \
        menu.MenuOption("Press Enter to Continue...", [lambda: state_stack.pop_to_main_menu()])

    continue_menu = menu.StaticMenu((0, 0), [continue_option], state_stack,
                                    margin=style.menu_theme.margin, may_escape=False)

    short_vspace = gui.VerticalSpace(7)
    long_vspace = gui.VerticalSpace(settings.SCREEN_HEIGHT - 22)

    victory_stack_panel.append(short_vspace)
    victory_stack_panel.append(line)
    victory_stack_panel.append(victory_text)
    victory_stack_panel.append(line)
    victory_stack_panel.append(ironic_text)
    victory_stack_panel.append(long_vspace)
    victory_stack_panel.append(continue_menu)

    grayout_rect = gui.RectangleChangeColor(rectfactory.full_screen_rect(), colors.DARK_BROWN, colors.YELLOW_D)

    ui_elements = [grayout_rect, victory_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


def game_over_screen(state_stack):
    game_over_stack_panel = gui.StackPanelVertical((0, 0), alignment=gui.StackPanelVertical.ALIGN_CENTER)
    red_line = gui.HorizontalLine(graphic.GraphicChar(None, colors.RED, icon.H_LINE), settings.SCREEN_WIDTH + 1)
    game_over_text = gui.TextBox("YOU DIED", (0, 0), colors.RED)
    insult_text = gui.TextBox("Like a bitch.", (0, 0), colors.DARK_BROWN)

    continue_option = \
        menu.MenuOption("Press Enter to Accept Your Fate...",
                        [lambda: state_stack.pop_to_main_menu()])

    continue_menu = menu.StaticMenu((0, 0), [continue_option], state_stack,
                                    margin=style.menu_theme.margin, may_escape=False)

    short_vspace = gui.VerticalSpace(7)
    long_vspace = gui.VerticalSpace(settings.SCREEN_HEIGHT - 22)

    game_over_stack_panel.append(short_vspace)
    game_over_stack_panel.append(red_line)
    game_over_stack_panel.append(game_over_text)
    game_over_stack_panel.append(red_line)
    game_over_stack_panel.append(insult_text)
    game_over_stack_panel.append(long_vspace)
    game_over_stack_panel.append(continue_menu)

    grayout_rect = gui.RectangleChangeColor(rectfactory.full_screen_rect(),
                                            colors.BLACK, colors.DARK_PURPLE)

    ui_elements = [grayout_rect, game_over_stack_panel]
    ui_state = state.UIState(gui.UIElementList(ui_elements))
    return ui_state


class DelayedStatePush(object):
    def __init__(self, state_stack, state):
        self.state_stack = state_stack
        self.state = state

    def __call__(self):
        self.state_stack.push(self.state)
