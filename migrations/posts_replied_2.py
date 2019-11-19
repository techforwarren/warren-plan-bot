import click
from google.cloud import firestore


@click.command()
@click.option(
    "--project",
    envvar="GCP_PROJECT",
    default="wpb-dev",
    type=str,
    help="gcp project where firestore db lives",
)
@click.option(
    "--dry-run",
    default=False,
    is_flag=True,
    help="run a dry run before executing the migration",
)
def run_migration(project="wpb-dev", dry_run=False):

    db = firestore.Client(project=project)

    posts_db = db.collection("posts")

    for post in posts_db.where("replied", "==", True).stream():
        post_id = post.id
        post = post.to_dict()
        post_record_update = {}
        if not post.get("processed"):
            post_record_update["processed"] = True

        if post_record_update:
            if dry_run:
                print(
                    f"[dry-run] For post: {post_id}\n[dry-run] With content:{post}\n[dry-run] Would update {post_record_update}"
                )
            else:
                print(
                    f"For post: {post_id}\n[dry-run] With content:{post}\n[dry-run] Updating {post_record_update}"
                )
                # partial update of record
                posts_db.document(post_id).update(post_record_update)


if __name__ == "__main__":
    run_migration()
