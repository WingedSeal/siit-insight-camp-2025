from .map import Block, Exit, Player, Spike, Tile


def map_maker(
    map_str: str,
    replacement_list: list[Tile] = [],
    replacement_dict: dict[str, list[Tile]] = {},
) -> list[list[Tile | None]]:
    """
    Input map in form of string instead.

    :param map_str: Multiline string

        - "X" = Block

        - "E" = Exit

        - " " = None (Floor)

        - "S" = Spike

        - "P" = Player

        - "\\_" means use the nth item in the `replacement_list`

    :param replacement_list: List of replacement tile to replace "_", defaults to []
    :param replacement_dict: Custom replacement tile for custom letter, defaults to {}
    :return: Array for map
    """
    if "_" in replacement_dict:
        raise ValueError("'_' can't be a key in replacement_dict")
    assert map_str[0] == "\n"
    assert map_str[-1] == "\n"
    map_str = map_str[1:-1]
    index = 0
    array: list[list[Tile | None]] = []
    for row_str in map_str.split("\n"):
        row: list[Tile | None] = []
        for tile_str in row_str:
            match tile_str:
                case "X":
                    row.append(Block())
                case "E":
                    row.append(Exit())
                case " ":
                    row.append(None)
                case "S":
                    row.append(Spike())
                case "P":
                    row.append(Player())
                case "_":
                    row.append(replacement_list[index])
                    index += 1
                case T:
                    row.append(replacement_dict[T].pop(0))
        array.append(row)
    if index != len(replacement_list):
        raise ValueError(
            f"Unused items in replacement_list (used {index} out of {len(replacement_list)})"
        )
    for dict_key, dict_list in replacement_dict.items():
        if dict_list:
            raise ValueError(
                f"Unused items in replacement_dict '{dict_key}' ({len(dict_list)} left unused)"
            )
    return array
