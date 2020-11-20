import obspy.core.inventory.util as obspy_util


def create_comments(temp):

    # gerer le cas de str et dict (pour le champ processing)
    if type(temp) in [str, dict]:
        return [obspy_util.Comment(temp)]
    comments = []
    for id, comment in enumerate(temp):
        value = comment["value"] if "value" in comment else comment
        begin_effective_time = (
            comment["BeginEffectiveTime"] if "BeginEffectiveTime" in comment else None
        )
        end_effective_time = (
            comment["EndEffectiveTime"] if "EndEffectiveTime" in comment else None
        )
        authors = create_authors(comment) if "authors" in comment else None
        comments.append(
            obspy_util.Comment(
                value,
                begin_effective_time=begin_effective_time,
                end_effective_time=end_effective_time,
                authors=authors,
            )
        )
    return comments


def create_authors(comment):

    authors = []
    for author in comment["authors"]:
        names = list(author["names"]) if "names" in author else None
        emails = list(author["emails"]) if "emails" in author else None
        agencies = list(author["agencies"]) if "agencies" in author else None
        phones = create_phoneNumber(author["phones"]) if "phones" in author else None
        authors.append(obspy_util.Person(names, agencies, emails, phones))

    return authors


def create_phoneNumber(phones):
    phonesObjects = []
    for phone in phones:
        country_code = phone["countryCode"] if "countryCode" in phone else None
        area_code = phone["areaCode"] if "areaCode" in phone else None
        phone_number = phone["phoneNumber"] if "phoneNumber" in phone else None
        description = phone["description"] if "description" in phone else None
        phonesObjects.append(
            obspy_util.PhoneNumber(area_code, phone_number, country_code, description)
        )

    return phonesObjects
