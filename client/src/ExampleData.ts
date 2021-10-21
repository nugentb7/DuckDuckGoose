import { UserRecord } from "./routes/admin/UserRecord";

/**
 * Sample user records for the admin page
 */
export const records: UserRecord[] = [
  {
    userId: 1,
    firstName: "Mary",
    lastName: "Burnham",
    email: "burnham23@s.r.e",
    registerDate: "9/12/20",
    moviesWatched: 5,
    visits: 4,
    watchedMovies: [
      {
        title: "Lord of the Rings: The Two Towers",
        genre: "Adventure Fantasy",
        userRating: 5,
      },
      {
        title: "Lord of the Rings: The Fellowship of the Ring",
        genre: "Adventure Fantasy",
        userRating: 4,
      },
      {
        title: "Lord of the Rings: The Return of the King",
        genre: "Adventure Fantasy",
        userRating: 5,
      },
      {
        title: "Lord of the Rings: The Fellowship of the Ring",
        genre: "Adventure Fantasy",
        userRating: 4,
      },
      {
        title: "Toy Story",
        genre: "Animation",
        userRating: 5,
      },
      {
        title: "Midsommar",
        genre: "Horror/Drama",
        userRating: 4,
      },
      {
        title: "Hereditary",
        genre: "Horror/Drama",
        userRating: 3,
      },
      {
        title: "The Adventures of Sharkboy and Lavagirl",
        genre: "Family/Adventure",
        userRating: 2,
      },
    ],
  },
  {
    userId: 2,
    firstName: "John",
    lastName: "Doe",
    email: "doeJ71@s.r.e",
    registerDate: "9/12/20",
    moviesWatched: 2,
    visits: 1,
    watchedMovies: [
      {
        title: "Lord of the Rings: The Fellowship of the Ring",
        genre: "Adventure Fantasy",
        userRating: 4,
      },
      {
        title: "Toy Story",
        genre: "Animation",
        userRating: 5,
      },
      {
        title: "Midsommar",
        genre: "Horror/Drama",
        userRating: 4,
      },
    ],
  },
  {
    userId: 3,
    firstName: " Umang",
    lastName: "Doshi",
    email: "doshiU22@s.r.e",
    registerDate: "9/14/20",
    moviesWatched: 3,
    visits: 2,
    watchedMovies: [
      {
        title: "Hereditary",
        genre: "Horror/Drama",
        userRating: 3,
      },
      {
        title: "The Adventures of Sharkboy and Lavagirl",
        genre: "Family/Adventure",
        userRating: 2,
      },
    ],
  },
];
// let movieRecords: WatchedMovie[] = [
//     {
//         title: "Avengers Endgame (2019)",
//         genre: "Action",
//         userRating: 5
//     },
//     {
//         title: "Goon (2011)",
//         genre: "Adventure",
//         userRating: 3
//     },
//     {
//         title: "Justice League (2017)",
//         genre: "Action",
//         userRating: 3.5
//     }
// ];
export const sampleRecord = records[0];

// export const BIG_USER_DATA: User[] = [];
// for (let i = 0; i < 10000; i++) {
//     BIG_USER_DATA.push({
//         id: i,
//         firstName: `First${i}`,
//         lastName: `Last${i}`,
//         email: 'exampleemail@email.com',
//         isAdmin: i % 2 === 0,
//         movies: [],
//         ratings: [],
//         tags: [],
//     });
// }
