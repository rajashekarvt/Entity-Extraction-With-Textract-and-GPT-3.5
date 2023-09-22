
system_role = f"""Extract Entities From The Given Text. Extract Them as a Key-Value Pair and Seperate Them On a New Line. Note That Every Key must have a value, Thus Extract Entities if and only if this condition holds true."""

example_input_1 = """OCR Text:
Jordan Bressler/Lorillard/MLBA To "Adam Goldfarb" agoldfar@newyork.bozell.com 03/13/2002 08:22 AM cc bcc Subject Re: HIU Special Event Baseboards Agreed Let's proceed. I would like to know if we've received any feedback on the makeup HIU plans to do for the delay on getting the special event available??? "Adam Goldfarb" Sagoldfar@newyork.bozell.com> on 03/12/2002 07:10:34 PM OF To: Jordan Bressler/Lorillard/MLBA@MLBA CC Courtney Hamill <chamil@newyork bozell com> Subject HIU Special Event Baseboards Jordan, as you know. all of the baskets in our special event will have baseboard banners displaying our print creative Attached are 6 jpegs with mockups of each Vc are fine with all of then except for Conic Book Woman and Eggshell Mosaic We've instructed their designers to crop into the ad images so that the black borders are eliminated I welcome your feedback on this material Many thanks. Adam - Collage Girl Baseboard.jpg - Comic Book Woman Baseboard.jpg - Guy with Dog Baseboard.jpg - Skateboard kid Baseboard jpg - Eggshell Basebcard.jpg - Exploding Head Baseboard.jpg 81873241"""

example_output_1 = """Entities:
From: Jordan Bressler
To: Adam Goldfarb
Date: 03/13/2002
Time: 08:22 AM
Description: Jordan, as you know. all of the baskets in our special event will have baseboard banners displaying our print creative Attached are 6 jpegs with mockups of each Vc are fine with all of then except for Conic Book Woman and Eggshell Mosaic We've instructed their designers to crop into the ad images so that the black borders are eliminated I welcome your feedback on this material Many thanks, Adam.
Additional Information: Collage Girl Baseboard.jpg,Comic Book Woman Baseboard.jpg,Guy with Dog Baseboard.jpg,Skateboard kid Baseboard jpg,Eggshell Basebcard.jpg,Exploding Head Baseboard.jpg"""