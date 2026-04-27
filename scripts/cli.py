import argparse
import json
import sys

from .api import MTeamAPI, format_size


def cmd_search(api, args):
    result, err = api.search(args.keyword, args.mode, args.page, args.pagesize)
    if err:
        print(f"❌ {err}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    items = result["items"]
    total = result["total"]
    page = result["page"]

    if not items:
        print(f"未找到与「{args.keyword}」(mode={args.mode}) 相关的结果。")
        return

    print(f"🔍 「{args.keyword}」(mode={args.mode})")
    print(f"共 {total} 条  |  第 {page} 页，显示 {len(items)} 条")
    print("-" * 50)

    for item in items:
        tid = item.get("id", "?")
        name = item.get("name") or item.get("title") or "(无标题)"
        size = format_size(item.get("size"))
        labels = ", ".join(item.get("labelsNew") or []) or "-"
        imdb = item.get("imdbRating") or "-"
        douban = item.get("doubanRating") or "-"
        status = item.get("status") or {}
        seeders = status.get("seeders", "?")
        leechers = status.get("leechers", "?")
        discount = status.get("discount", "-")

        print(
            f"[{tid}] {name}\n"
            f"  大小: {size}  |  做种: {seeders}  |  下载中: {leechers}\n"
            f"  标签: {labels}  |  折扣: {discount}\n"
            f"  IMDB: {imdb}  |  豆瓣: {douban}"
        )


def cmd_detail(api, args):
    item, err = api.detail(args.torrent_id)
    if err:
        print(f"❌ {err}", file=sys.stderr)
        sys.exit(1)

    tid = item.get("id", args.torrent_id)
    name = item.get("name") or item.get("title") or "(无标题)"
    descr = item.get("smallDescr") or "-"
    size = format_size(item.get("size"))
    numfiles = item.get("numfiles", "?")
    labels = ", ".join(item.get("labelsNew") or []) or "-"
    imdb = item.get("imdb") or "-"
    imdb_rating = item.get("imdbRating") or "-"
    douban = item.get("douban") or "-"
    douban_rating = item.get("doubanRating") or "-"
    created = item.get("createdDate", "-")
    status = item.get("status") or {}
    seeders = status.get("seeders", "?")
    leechers = status.get("leechers", "?")
    completed = status.get("timesCompleted", "?")
    discount = status.get("discount", "-")
    visible = status.get("visible", True)
    banned = status.get("banned", False)

    print(f"📀 [{tid}] {name}")
    print("=" * 60)
    print(f"简介      : {descr}")
    print(f"大小      : {size}  ({numfiles} 个文件)")
    print(f"标签      : {labels}")
    print(f"折扣      : {discount}")
    print(f"做种      : {seeders}  |  下载中: {leechers}  |  完成: {completed}")
    print(f"发布时间  : {created}")
    print(f"可见      : {visible}  |  已禁: {banned}")
    print(f"IMDB      : {imdb}  |  评分: {imdb_rating}")
    print(f"豆瓣      : {douban}  |  评分: {douban_rating}")


def cmd_download(api, args):
    path, err = api.download(args.torrent_id, args.dir)
    if err:
        print(f"❌ {err}", file=sys.stderr)
        sys.exit(1)
    print(f"✅ 已下载: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="M-Team 影视资源搜索与下载 CLI",
        prog="mteam-search",
    )
    sub = parser.add_subparsers(dest="command")

    p_search = sub.add_parser("search", help="搜索 torrent")
    p_search.add_argument("keyword", help="搜索关键词")
    p_search.add_argument("--mode", default="normal",
                          help="搜索模式 (normal, movie, tvshow, anime, music, adult, all)")
    p_search.add_argument("--page", type=int, default=1)
    p_search.add_argument("--pagesize", type=int, default=20)
    p_search.add_argument("--json", action="store_true", help="输出原始 JSON")
    p_search.set_defaults(func=cmd_search)

    p_detail = sub.add_parser("detail", help="查看 torrent 详情")
    p_detail.add_argument("torrent_id", help="Torrent ID")
    p_detail.set_defaults(func=cmd_detail)

    p_dl = sub.add_parser("download", help="下载 .torrent 文件")
    p_dl.add_argument("torrent_id", help="Torrent ID")
    p_dl.add_argument("--dir", default="./seed", help="下载目录")
    p_dl.set_defaults(func=cmd_download)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    try:
        api = MTeamAPI()
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    args.func(api, args)


if __name__ == "__main__":
    main()
