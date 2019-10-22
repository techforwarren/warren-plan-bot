plan_id_transforms = [
    {"old_id": "anti_corruption", "new_id": "anti_corruption"},
    {"old_id": "student_debt_free_college", "new_id": "affordable_higher_education"},
    {"old_id": "immigration_reform", "new_id": "immigration"},
    {"old_id": "wall_street_reform", "new_id": "wall_street"},
    {"old_id": "stop_economy_crash", "new_id": "stop_economic_crash"},
    {"old_id": "climate_risk_disclosure", "new_id": "clean_energy"},
    {"old_id": "women_of_color_economic", "new_id": "valuing_work_women_of_color"},
    {"old_id": "foreign_service", "new_id": "rebuild_the_state_department"},
    {"old_id": "election_reform", "new_id": "strengthening_democracy"},
    {"old_id": "private_prison_reform", "new_id": "end_private_prisons"},
    {"old_id": "minority_businesses", "new_id": "leveling_field_entrepreneurs_color"},
    {"old_id": "economic_patriotism", "new_id": "american_jobs"},
    {"old_id": "green_manufacturing", "new_id": "green_manufacturing"},
    {
        "old_id": "presidential_accountability",
        "new_id": "no_president_is_above_the_law",
    },
    {"old_id": "reproductive_rights", "new_id": "protect_womens_choices"},
    {"old_id": "defense_lobbyists", "new_id": "corporate_influence_pentagon"},
    {
        "old_id": "national_security_climate_change",
        "new_id": "military_combat_climate_change",
    },
    {"old_id": "opioid_crisis", "new_id": "end_opioid_crisis"},
    {"old_id": "puerto_rico_debt_relief", "new_id": "puerto_rico_debt_relief"},
    {"old_id": "black_maternal_mortality", "new_id": "black_women_mortality_essence"},
    {"old_id": "military_housing", "new_id": "improve_military_housing"},
    {"old_id": "public_land", "new_id": "protect_public_lands"},
    {"old_id": "corporate_taxes", "new_id": "real_corporate_profits"},
    {
        "old_id": "corporate_executive_accountability",
        "new_id": "time_to_scare_corporate_america_straight",
    },
    {"old_id": "family_farms", "new_id": "americas_family_farmers"},
    {"old_id": "electoral_college", "new_id": "electoral_college"},
    {"old_id": "affordable_housing", "new_id": "safe_affordable_housing"},
    {"old_id": "break_up_big_tech", "new_id": "break_up_big_tech"},
    {"old_id": "universal_child_care", "new_id": "universal_child_care"},
    {"old_id": "ultra_millionaire_tax", "new_id": "ultra_millionaire_tax"},
    {"old_id": "new_farm_economy", "new_id": "new_farm_economy"},
    {"old_id": "gun_violence", "new_id": "gun_violence"},
    {"old_id": "invest_in_rural_america", "new_id": "invest_rural"},
    {"old_id": "tribal_nations_and_indigenous_peoples", "new_id": "tribal_nations"},
    {
        "old_id": "comprehensive_criminal_justice_reform",
        "new_id": "criminal_justice_reform",
    },
    {"old_id": "trade_on_our_terms", "new_id": "new_approach_trade"},
    {"old_id": "clean_energy_for_america", "new_id": "100_clean_energy"},
    {"old_id": "expanding_social_security", "new_id": "social_security"},
    {"old_id": "health_care", "new_id": "health_care"},
    {"old_id": "lgbtq_equality", "new_id": "lgtbtq_equality"},
    {"old_id": "disability_justice", "new_id": "disability_justice"},
    {"old_id": "competitive_markets", "new_id": "promoting_competitive_markets"},
    {"old_id": "accountable_capitalism", "new_id": "accountable_capitalism"},
    {"old_id": "veterans", "new_id": "veterans"},
    {"old_id": "foreign_policy", "new_id": "foreign_policy"},
    {"old_id": "climate_change", "new_id": "climate_change"},
    {"old_id": "wall_street_accountable", "new_id": "holding_wall_street_accountable"},
    {"old_id": "end_washington_corruption", "new_id": "end_washington_corruption"},
    {"old_id": "congressional_independence", "new_id": "congressional_independence"},
    {"old_id": "excessive_lobbying_tax", "new_id": "excessive_lobbying_tax"},
    {
        "old_id": "american_workers_raising_wages",
        "new_id": "empowering_american_workers",
    },
    {"old_id": "restore_trust_in_ethical_judiciary", "new_id": "restore_trust"},
    {"old_id": "environmental_justice", "new_id": "environmental_justice"},
    {"old_id": "campaign_finance_reform", "new_id": "campaign_finance_reform"},
]

id_lookup = {d["old_id"]: d["new_id"] for d in plan_id_transforms}

# import json
# from os import path
#
# DIRNAME = path.dirname(path.realpath(__file__))
#
# with open(path.join(DIRNAME, "../scripts/labeled_posts.json")) as posts_file:
#     posts = json.load(posts_file)
#
# labeled_posts = []
#
# for post in posts:
#     labeled_post = post
#     if labeled_post["match"]:
#         labeled_post["match"] = id_lookup[labeled_post["match"]]
#     if "alternative_matches" in labeled_post:
#         labeled_post["alternative_matches"] = [
#             id_lookup[match] for match in labeled_post["alternative_matches"]
#         ]
#     labeled_posts.append(labeled_post)
#
# print(labeled_posts)
#
# with open(path.join(DIRNAME, "../scripts/labeled_posts.json"), "w") as posts_file:
#     json.dump(labeled_posts, posts_file, indent=2, separators=(",", ": "))
