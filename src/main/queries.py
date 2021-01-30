
fetch_transaction_to_query = """SELECT transaction_id, user_to, amount, paid_on FROM payments_data 
                                INNER JOIN users ON users.id = payments_data.user_from 
                                WHERE users.id = {} 
                                GROUP BY transaction_id 
                                ORDER BY paid_on DESC"""

fetch_transaction_from_query = """SELECT transaction_id, user_from, amount, paid_on FROM payments_data 
                                INNER JOIN users ON users.id = payments_data.user_to 
                                WHERE users.id = {} 
                                GROUP BY transaction_id 
                                ORDER BY paid_on DESC"""


fetch_owe_from = """SELECT ticket_id, user_to, amount, made_on FROM owing_data
                    INNER JOIN users ON users.id = owing_data.user_from
                    WHERE users.id ={}
                    GROUP BY ticket_id
                    ORDER BY made_on DESC;"""

fetch_owe_to = """SELECT ticket_id, user_from, amount, made_on FROM owing_data
                    INNER JOIN users ON users.id = owing_data.user_to
                    WHERE users.id ={}
                    GROUP BY ticket_id
                    ORDER BY made_on DESC;"""

